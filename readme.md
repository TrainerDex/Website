==Fix Label==

The label is how django knows what app you're referring to.

To ensure django doesn't re-run all the migrations for this app, we
must update the migration-run history in the database with raw SQL:

    UPDATE django_migrations
       SET app = 'pokemongo'
     WHERE app = 'trainer';

We can't use a normal migration for this unfortunately. I recommend
using `./manage.py dbshell`.

Also, to ensure existing model definitions and migrations don't break,
we need to change their "shop" references to "catalogue".

Finally, to ensure that generic foreign keys (such as in django's
permissions system) continue to work, we need to update the
`django_content_type` table:

    UPDATE django_content_type
       SET app_label = 'pokemongo'
     WHERE app_label = 'trainer';

From now on, new db tables created in this app get the new default
prefix of "pokemongo_".

`python manage.py cities --import=alt_name,country,region,continent`

`python manage.py makemessages --no-wrap --ignore=env/* -l de -l es -l fr -l it -l ja -l ko -l pt-br -l zh-hant`
