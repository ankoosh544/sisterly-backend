# Generated by Django 3.2.4 on 2021-07-29 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_app', '0002_order_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='description',
            field=models.CharField(default='', max_length=3000, verbose_name='Descrizione'),
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=models.PositiveSmallIntegerField(choices=[(1, 'WAITING FOR ACCEPTANCE'), (2, 'WAITING FOR PAYMENT'), (3, 'IN_TRANSIT'), (4, 'BORROWED'), (5, 'IN_RETURN_TO_THE_LENDER'), (6, 'REJECTED')], default=1),
        ),
    ]