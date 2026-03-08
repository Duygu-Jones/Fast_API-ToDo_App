from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM, get_current_user
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException


# get_db fonksiyonunu override ederek, test veritabanı bağlantısını sağlar
app.dependency_overrides[get_db] = override_get_db



# ===================================================================== 
# auth.py dosyasındaki "authenticate_user" fonksiyonunun test edilmesi
def test_authenticate_user(test_user):
    db = TestingSessionLocal() # test veritabanı bağlantısı oluşturuluyor

    authenticated_user = authenticate_user(test_user.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    # authenticate_user fonksiyonu, olmayan bir kullanıcı adıyla, dogru 'testpassword' şifresiyle çağrılıyor
    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    # authenticate_user fonksiyonu, doğru kullanıcı adıyla, yanlış şifre ile çağrılıyor
    wrong_password_user = authenticate_user(test_user.username, 'wrongpassword', db)
    assert wrong_password_user is False


# Bu test, kimlik doğrulama fonksiyonunun aşağıdaki özelliklere sahip olduğunu doğrular:

# Pozitif Durum: Doğru kimlik bilgileriyle girişin başarılı olduğunu ve doğru kullanıcıyı döndürdüğünü
# Negatif Durum 1: Olmayan bir kullanıcı için uygun şekilde başarısızlık döndürdüğünü
# Negatif Durum 2: Yanlış şifre için uygun şekilde başarısızlık döndürdüğünü

# Bu, güvenlik açısından kritik bir fonksiyonun tüm olası durumları 
# doğru şekilde ele aldığından emin olmak için kapsamlı bir test sağlar. 
# Böylece, uygulamanızın kimlik doğrulama sisteminin beklenen şekilde çalıştığından emin olabilirsiniz.


# =====================================================================
# auth.py dosyasındaki "create_access_token" fonksiyonunun test edilmesi
def test_create_access_token():
    # Test için kullanılacak örnek veriler tanımlanıyor
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1) # geçerlilik süresi 1 gün

    # Test edilecek fonksiyon (create_access_token) çağrılıyor, ve oluşturulan fake "token" değişkende saklanıyor
    token = create_access_token(username, user_id, role, expires_delta)
    
    # Oluşturulan token, jose kütüphanesinin jwt.decode fonksiyonu ile çözülüyor
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                                options={'verify_signature': False})
                                # options={'verify_signature': False} parametresi, 
                                # imza doğrulamasını devre dışı bırakır (sadece içeriği test etmek için)

    # Çözülen token'daki bilgilerin beklenen değerlerle eşleştiğini kontrol eder:
    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role




# =====================================================================
# Bu `@pytest.mark.asyncio` dekoratör, pytest'e bu fonksiyonun asenkron olduğunu ve 
# asyncio tabanlı bir test koşucusu kullanılması gerektiğini belirtir
# `pytest-asyncio` eklentisi yüklü olmalıdır

# Bu test, `create_access_token` fonksiyonunun aşağıdaki özelliklere sahip olduğunu doğrular:
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Test için gerekli JWT token oluşturuluyor
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token) # oluşturulan token ile fonk çağrılıyor 
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}
    # Asenkron fonksiyonları çağırmak için `await` kullanmanız gerekir, 
    # ve await sadece `async` fonksiyonlar içinde kullanılabilir.

# FastAPI, Starlette çerçevesini temel alan ve ASGI (Asynchronous Server Gateway Interface)
# protokolünü kullanan bir web çerçevesidir. 
# Bu nedenle, tüm bağımlılık enjeksiyon fonksiyonları (get_current_user gibi) 
# genellikle async def olarak tanımlanır ve bu fonksiyonları test etmek için de 
# asenkron test fonksiyonları yazmanız gerekir.



# =====================================================================
# Bu test, JWT token içinde gerekli bilgiler eksikse get_current_user fonksiyonunun doğru hata fırlatmasını kontrol ediyor.
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    # Eksik bilgiler içeren bir token oluşturuluyor (sub ve id bilgileri eksik)
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Could not validate user.'

# Bu test, kimlik doğrulama sisteminin eksik veya hatalı token'ları düzgün şekilde reddedip etmediğini doğrular. 
# Güvenlik açısından önemlidir çünkü geçersiz token'ların uygun şekilde işlenmesi gerekir.