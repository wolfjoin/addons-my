#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of connector, an Odoo module.
#
#     Author: Stéphane Bidoul <stephane.bidoul@acsone.eu>
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     connector is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     connector is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with connector.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
"""
What is the job runner?
-----------------------
This is an alternative to connector workers, with the goal
of resolving issues due to the polling nature of workers:

* jobs do not start immediately even if there is a free connector worker,
* connector workers may starve while other workers have too many jobs enqueued,
* connector workers require another startup script,
  making deployment more difficult

It is fully compatible with the connector mechanism and only
replaces workers.

How does it work?
-----------------

* It starts as a thread in the Odoo main process
* It receives postgres NOTIFY messages each time jobs are
  added or updated in the queue_job table.
* It maintains an in-memory priority queue of jobs that
  is populated from the queue_job tables in all databases.
* It does not run jobs itself, but asks Odoo to run them through an
  anonymous ``/connector/runjob`` HTTP request. [1]_

How to use it?
--------------

* Set the following environment variables:

  - ``ODOO_CONNECTOR_CHANNELS=root:4`` (or any other channels configuration)
  - optional if ``xmlrpc_port`` is not set: ``ODOO_CONNECTOR_PORT=8069``

* Or alternatively, set ``channels = root:4`` in the ``[options-connector]``
  section of the odoo configuration file.

* Start Odoo with ``--load=web,web_kanban,connector``
  and ``--workers`` greater than 1. [2]_

* Confirm the runner is starting correctly by checking the odoo log file:

.. code-block:: none

  ...INFO...connector.jobrunner.runner: starting
  ...INFO...connector.jobrunner.runner: initializing database connections
  ...INFO...connector.jobrunner.runner: connector runner ready for db <dbname>
  ...INFO...connector.jobrunner.runner: database connections ready

* Disable the "Enqueue Jobs" cron.

* Do NOT start openerp-connector-worker.

* Create jobs (eg using base_import_async) and observe they
  start immediately and in parallel.

* Tip: to enable debug logging for the connector, use
  ``--log-handler=openerp.addons.connector:DEBUG``

Caveat
------

* After creating a new database or installing connector on an
  existing database, Odoo must be restarted for the runner to detect it.

* When Odoo shuts down normally, it waits for running jobs to finish.
  However, when the Odoo server crashes or is otherwise force-stopped,
  running jobs are interrupted while the runner has no chance to know
  they have been aborted. In such situations, jobs may remain in
  ``started`` or ``enqueued`` state after the Odoo server is halted.
  Since the runner has no way to know if they are actually running or
  not, and does not know for sure if it is safe to restart the jobs,
  it does not attempt to restart them automatically. Such stale jobs
  therefore fill the running queue and prevent other jobs to start.
  You must therefore requeue them manually, either from the Jobs view,
  or by running the following SQL statement *before starting Odoo*:

.. code-block:: sql

  update queue_job set state='pending' where state in ('started', 'enqueued')

.. rubric:: Footnotes

.. [1] From a security standpoint, it is safe to have an anonymous HTTP
       request because this request only accepts to run jobs that are
       enqueued.
.. [2] It works with the threaded Odoo server too, although this way
       of running Odoo is obviously not for production purposes.
"""

from contextlib import closing
import logging
import os
import re
import select
import threading
import time

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import requests

import openerp
from openerp.tools import config

from .channels import ChannelManager, PENDING, ENQUEUED, NOT_DONE

SELECT_TIMEOUT = 60
ERROR_RECOVERY_DELAY = 5

_logger = logging.getLogger(__name__)

sessions = {}


# Unfortunately, it is not possible to extend the Odoo
# server command line arguments, so we resort to environment variables
# to configure the runner (channels mostly).
#
# On the other hand, the odoo configuration file can be extended at will,
# so we check it in addition to the environment variables.


def _channels():
    # environment takes precedence over config file if set.
    # If set to "" will disable the runner.
    env_channels = os.environ.get('ODOO_CONNECTOR_CHANNELS', None)
    return (
        env_channels if env_channels is not None
        else config.misc.get("options-connector", {}).get("channels")
    )


def _async_http_get(port, db_name, job_uuid):
    if not sessions.get(db_name):
        sessions[db_name] = requests.Session()
    session = sessions[db_name]
    if not session.cookies:
        # obtain an anonymous session
        _logger.info("obtaining an anonymous session for the job runner")
        url = 'http://localhost:%s/web/login?db=%s' % (port, db_name)
        response = session.get(url, timeout=30)
        response.raise_for_status()

    # Method to set failed job (due to timeout, etc) as pending,
    # to avoid keeping it as enqueued.
    def set_job_pending():
        conn = psycopg2.connect(openerp.sql_db.dsn(db_name)[1])
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with closing(conn.cursor()) as cr:
            cr.execute(
                "UPDATE queue_job SET state=%s, "
                "date_enqueued=NULL, date_started=NULL "
                "WHERE uuid=%s and state=%s", (PENDING, job_uuid, ENQUEUED)
            )

    # TODO: better way to HTTP GET asynchronously (grequest, ...)?
    #       if this was python3 I would be doing this with
    #       asyncio, aiohttp and aiopg
    def urlopen():
        url = ('http://localhost:%s/connector/runjob?db=%s&job_uuid=%s' %
               (port, db_name, job_uuid))
        try:
            # we are not interested in the result, so we set a short timeout
            # but not too short so we trap and log hard configuration errors
            response = session.get(url, timeout=1)

            # raise_for_status will result in either nothing, a Client Error
            # for HTTP Response codes between 400 and 500 or a Server Error
            # for codes between 500 and 600
            response.raise_for_status()
        except requests.Timeout:
            set_job_pending()
        except:
            _logger.exception("exception in GET %s", url)
            session.cookies.clear()
            set_job_pending()
    thread = threading.Thread(target=urlopen)
    thread.daemon = True
    thread.start()


class Database(object):

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = psycopg2.connect(openerp.sql_db.dsn(db_name)[1])
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.has_connector = self._has_connector()
        if self.has_connector:
            self.has_channel = self._has_queue_job_column('channel')
            self._initialize()

    def close(self):
        try:
            self.conn.close()
        except:
            pass
        self.conn = None

    def _has_connector(self):
        with closing(self.conn.cursor()) as cr:
            try:
                cr.execute("SELECT 1 FROM ir_module_module "
                           "WHERE name=%s AND state=%s",
                           ('connector', 'installed'))
            except psycopg2.ProgrammingError as err:
                if unicode(err).startswith('relation "ir_module_module" '
                                           'does not exist'):
                    return False
                else:
                    raise
            return cr.fetchone()

    def _has_queue_job_column(self, column):
        if not self.has_connector:
            return False
        with closing(self.conn.cursor()) as cr:
            cr.execute("SELECT 1 FROM information_schema.columns "
                       "WHERE table_name=%s AND column_name=%s",
                       ('queue_job', column))
            return cr.fetchone()

    def _initialize(self):
        with closing(self.conn.cursor()) as cr:
            # this is the trigger that sends notifications when jobs change
            cr.execute("""
                DROP TRIGGER IF EXISTS queue_job_notify ON queue_job;

                CREATE OR REPLACE
                    FUNCTION queue_job_notify() RETURNS trigger AS $$
                BEGIN
                    IF TG_OP = 'DELETE' THEN
                        IF OLD.state != 'done' THEN
                            PERFORM pg_notify('connector', OLD.uuid);
                        END IF;
                    ELSE
                        PERFORM pg_notify('connector', NEW.uuid);
                    END IF;
                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER queue_job_notify
                    AFTER INSERT OR UPDATE OR DELETE
                    ON queue_job
                    FOR EACH ROW EXECUTE PROCEDURE queue_job_notify();
            """)
            cr.execute("LISTEN connector")

    def select_jobs(self, where, args):
        query = ("SELECT %s, uuid, id as seq, date_created, "
                 "priority, eta, state "
                 "FROM queue_job WHERE %s" %
                 ('channel' if self.has_channel else 'NULL',
                  where))
        with closing(self.conn.cursor()) as cr:
            cr.execute(query, args)
            return list(cr.fetchall())

    def set_job_enqueued(self, uuid):
        with closing(self.conn.cursor()) as cr:
            cr.execute("UPDATE queue_job SET state=%s, "
                       "date_enqueued=date_trunc('seconds', "
                       "                         now() at time zone 'utc') "
                       "WHERE uuid=%s",
                       (ENQUEUED, uuid))


class ConnectorRunner(object):

    def __init__(self, port=8069, channel_config_string='root:1'):
        self.port = port
        self.channel_manager = ChannelManager()
        self.channel_manager.simple_configure(channel_config_string)
        self.db_by_name = {}
        self._stop = False
        self._stop_pipe = os.pipe()

    def get_db_names(self):
        if openerp.tools.config['db_name']:
            db_names = openerp.tools.config['db_name'].split(',')
        else:
            db_names = openerp.service.db.exp_list(True)
        dbfilter = openerp.tools.config['dbfilter']
        if dbfilter and '%d' not in dbfilter and '%h' not in dbfilter:
            db_names = [d for d in db_names if re.match(dbfilter, d)]
        return db_names

    def close_databases(self, remove_jobs=True):
        for db_name, db in self.db_by_name.items():
            try:
                if remove_jobs:
                    self.channel_manager.remove_db(db_name)
                db.close()
            except:
                _logger.warning('error closing database %s',
                                db_name, exc_info=True)
        self.db_by_name = {}

    def initialize_databases(self):
        for db_name in self.get_db_names():
            db = Database(db_name)
            if not db.has_connector:
                _logger.debug('connector is not installed for db %s', db_name)
            else:
                self.db_by_name[db_name] = db
                for job_data in db.select_jobs('state in %s', (NOT_DONE,)):
                    self.channel_manager.notify(db_name, *job_data)
                _logger.info('connector runner ready for db %s', db_name)

    def run_jobs(self):
        now = openerp.fields.Datetime.now()
        for job in self.channel_manager.get_jobs_to_run(now):
            if self._stop:
                break
            _logger.info("asking Odoo to run job %s on db %s",
                         job.uuid, job.db_name)
            self.db_by_name[job.db_name].set_job_enqueued(job.uuid)
            _async_http_get(self.port, job.db_name, job.uuid)

    def process_notifications(self):
        for db in self.db_by_name.values():
            while db.conn.notifies:
                if self._stop:
                    break
                notification = db.conn.notifies.pop()
                uuid = notification.payload
                job_datas = db.select_jobs('uuid = %s', (uuid,))
                if job_datas:
                    self.channel_manager.notify(db.db_name, *job_datas[0])
                else:
                    self.channel_manager.remove_job(uuid)

    def wait_notification(self):
        for db in self.db_by_name.values():
            if db.conn.notifies:
                return
        # wait for something to happen in the queue_job tables
        conns = [db.conn for db in self.db_by_name.values()]
        conns.append(self._stop_pipe[0])
        conns, _, _ = select.select(conns, [], [], SELECT_TIMEOUT)
        if conns and not self._stop:
            for conn in conns:
                conn.poll()

    def stop(self):
        _logger.info("graceful stop requested")
        self._stop = True
        # wakeup the select() in wait_notification
        os.write(self._stop_pipe[1], '.')

    def run(self):
        _logger.info("starting")
        while not self._stop:
            # outer loop does exception recovery
            try:
                _logger.info("initializing database connections")
                # TODO: how to detect new databases or databases
                #       on which connector is installed after server start?
                self.initialize_databases()
                _logger.info("database connections ready")
                # inner loop does the normal processing
                while not self._stop:
                    self.process_notifications()
                    self.run_jobs()
                    self.wait_notification()
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                # Interrupted system call, i.e. KeyboardInterrupt during select
                if isinstance(e, select.error) and e[0] == 4:
                    self.stop()
                else:
                    _logger.exception("exception: sleeping %ds and retrying",
                                      ERROR_RECOVERY_DELAY)
                    self.close_databases()
                    time.sleep(ERROR_RECOVERY_DELAY)
        self.close_databases(remove_jobs=False)
        _logger.info("stopped")
