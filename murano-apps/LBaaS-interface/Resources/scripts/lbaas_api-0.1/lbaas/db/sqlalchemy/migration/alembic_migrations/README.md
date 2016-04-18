The migrations in `alembic_migrations/versions` contain the changes needed to migrate
between Mistral database revisions. A migration occurs by executing a script that
details the changes needed to upgrade the database. The migration scripts
are ordered so that multiple scripts can run sequentially. The scripts are executed by
Mistral's migration wrapper which uses the Alembic library to manage the migration. Mistral
supports migration from Kilo or later.

You can upgrade to the latest database version via:
```
lbaas-db-manage --config-file /path/to/lbaas.conf upgrade head
```

You can populate the database with standard actions and workflows:
```
lbaas-db-manage --config-file /path/to/lbaas.conf populate
```

To check the current database version:
```
lbaas-db-manage --config-file /path/to/lbaas.conf current
```

To create a script to run the migration offline:
```
lbaas-db-manage --config-file /path/to/lbaas.conf upgrade head --sql
```

To run the offline migration between specific migration versions:
```
lbaas-db-manage --config-file /path/to/lbaas.conf upgrade <start version>:<end version> --sql
```

Upgrade the database incrementally:
```
lbaas-db-manage --config-file /path/to/lbaas.conf upgrade --delta <# of revs>
```

Or, upgrade the database to one newer revision:
```
lbaas-db-manage --config-file /path/to/lbaas.conf upgrade +1
```

Create new revision:
```
lbaas-db-manage --config-file /path/to/lbaas.conf revision -m "description of revision" --autogenerate
```

Create a blank file:
```
lbaas-db-manage --config-file /path/to/lbaas.conf revision -m "description of revision"
```

This command does not perform any migrations, it only sets the revision.
Revision may be any existing revision. Use this command carefully.
```
lbaas-db-manage --config-file /path/to/lbaas.conf stamp <revision>
```

To verify that the timeline does branch, you can run this command:
```
lbaas-db-manage --config-file /path/to/lbaas.conf check_migration
```

If the migration path has branch, you can find the branch point via:
```
lbaas-db-manage --config-file /path/to/lbaas.conf history