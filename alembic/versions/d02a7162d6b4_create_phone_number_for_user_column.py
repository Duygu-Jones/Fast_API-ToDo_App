"""Create phone number for user column

Revision ID: d02a7162d6b4
Revises: 
Create Date: 2025-02-26 10:17:56.225406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# sa: sqlalchemy kütüphanesinin kısa adı

# revision identifiers, used by Alembic.
# Bu tanımlayıcılar Alembic'in migration'ları takip etmesi için kullanılır
revision: str = 'd02a7162d6b4'  # Bu migration'ın benzersiz kimliği
down_revision: Union[str, None] = None  # Önceki migration'ın kimliği, None ise ilk migration
branch_labels: Union[str, Sequence[str], None] = None  # Branch etiketleri, genellikle None
depends_on: Union[str, Sequence[str], None] = None  # Bu migration'ın bağımlı olduğu diğer migration'lar


def upgrade() -> None:
   """
   İleri yönde migration - veritabanını günceller
   Bu fonksiyon çalıştığında 'users' tablosuna 'phone_number' adında yeni bir sütun ekler
   String tipinde ve nullable=True olarak ayarlanmıştır (boş değer kabul eder)
   """
   op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))


def downgrade() -> None:
   """
   Geri yönde migration - yapılan değişiklikleri geri alır
   Bu fonksiyon çalıştığında 'users' tablosundan 'phone_number' sütununu kaldırır
   Hata durumunda veya downgrade gerektiğinde kullanılır
   """
   op.drop_column('users', 'phone_number')