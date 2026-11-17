from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_rename_county_address_country'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'verbose_name_plural': 'addresses'},
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='address',
            name='line2',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
