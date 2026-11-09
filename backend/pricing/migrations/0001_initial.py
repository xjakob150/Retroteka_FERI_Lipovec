import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('listing_count', models.PositiveIntegerField()),
                ('source', models.CharField(choices=[('ebay', 'eBay')], default='ebay', max_length=10)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_checks', to='collection.collectionitem')),
            ],
            options={
                'ordering': ['-checked_at', '-id'],
            },
        ),
    ]
