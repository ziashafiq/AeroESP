# Hand-written rather than autodetected: `makemigrations` cannot tell
# a rename from a remove+add without an interactive prompt, and in
# non-interactive use it defaults to remove+add - which would drop
# error_codes_json's data (already copied from the old error_codes by
# 0007) the moment the old CharField is removed. Explicit RemoveField
# then RenameField preserves it.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('research_review', '0007_copy_error_codes_to_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expertreview',
            name='error_codes',
        ),
        migrations.RenameField(
            model_name='expertreview',
            old_name='error_codes_json',
            new_name='error_codes',
        ),
    ]
