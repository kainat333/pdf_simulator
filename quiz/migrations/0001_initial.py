from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_number', models.IntegerField(unique=True)),
                ('question_text', models.TextField()),
                ('option_a', models.TextField()),
                ('option_b', models.TextField()),
                ('option_c', models.TextField()),
                ('option_d', models.TextField()),
                ('correct_option', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1)),
                ('explanation', models.TextField()),
            ],
            options={
                'ordering': ['question_number'],
            },
        ),
        migrations.CreateModel(
            name='QuizSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('selected_questions', models.TextField()),
                ('user_answers', models.TextField(default='{}')),
                ('score', models.IntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('current_question_index', models.IntegerField(default=0)),
            ],
        ),
    ]
