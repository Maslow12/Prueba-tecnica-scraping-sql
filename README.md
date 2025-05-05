# Prueba Técnica: Scraping Web + Almacenamiento SQL (Perfil Mid-Level)
* By Sebastian Yusti

📋 Requisitos Previos
Python 3.13 instalado (Descargar Python: https://www.python.org/downloads/release/python-3133/)

🔧 Pasos para Instalar el Script:


1️⃣ Clonar el Repositorio (Opcional)


```
git clone https://github.com/Maslow12/Prueba-tecnica-scraping-sql.git
```

2️⃣ Crear un Entorno Virtual (Virtual Environment)
📌 Recomendado para evitar conflictos entre dependencias.

```
python -m venv venv
.\venv\Scripts\activate
```

3️⃣ Instalar Dependencias (requirements.txt)
Si el proyecto incluye un archivo requirements.txt:

```
pip install -r requirements.txt
```

4️⃣ Ejecutar el Script

```
python main.py
```

### Requirements:

```
beautifulsoup4==4.13.4
certifi==2025.4.26
charset-normalizer==3.4.2
free_proxy==1.1.3
idna==3.10
lxml==5.4.0
numpy==2.2.5
pandas==2.2.3
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.3
six==1.17.0
soupsieve==2.7
typing_extensions==4.13.2
tzdata==2025.2
urllib3==2.4.0
```

* __BeautifulSoup:__ Se optó por utilizar BeautifulSoup (BS4) para el scraping debido a la prueba no requiere un alcance complejo. No obstante, para proyectos más complejos o de mayor escala, Scrapy sería la opción recomendada, ya que ofrece una infraestructura robusta con funcionalidades avanzadas como manejo de peticiones concurrentes, pipelines integrados y soporte para crawling automatizado.
  
* __FreeProxy:__ Esta libreria no es recomendada para entornos productivos, ya que es mejor utilizar opciones pagas para obtener proxies. Su función principal es extraer proxies activos de sitios como sslproxies.org, us-proxy.org y free-proxy-list.net, verificando su disponibilidad para implementar un sistema de proxies rotativos. Dado que IMDB emplea Cloudflare para bloquear bots, y al no poder usar herramientas como Selenium o Playwright en este ejercicio, se optó por requests con proxies para evitar el bloqueo y extraer el HTML. Sin embargo, esta solución presenta limitaciones de rendimiento, las cuales se optimizaron mediante programación concurrente, combinando ThreadPoolExecutor para I/O y multiprocessing.Pool.

* __Pandas:__ Es la libreria que facilita exportar los datos desde un ```dict``` a un archivo .xslx

* __Sqlite3:__: Base de datos utilizada


### Notas:

* Un desafío técnico clave fue la imposibilidad de utilizar frameworks de automatización de navegadores (como Selenium o Playwright) para manejar la carga dinámica de contenido mediante scroll en JavaScript. Esto limitaba la visualización inicial a solo las primeras 25 películas, cuando el objetivo requería obtener al menos 50. Como solución alternativa, se implementó una estrategia basada en los parámetros de la URL: se extrajeron los primeros 25 resultados ordenados ascendentemente (```?sort=rank%2Casc```) y los últimos 25 ordenados descendentemente (```?sort=rank%2Cdesc```), combinando ambos conjuntos para alcanzar el volumen de datos deseado.
  
* Para estandarizar el formato de duración de las películas (que originalmente aparecía en horas y minutos), se implementó la función ```time_to_minutes(time_str:str)->int```, la cual convierte este dato a una representación numérica en minutos.

* Como se mencionó previamente, para optimizar el rendimiento del script se implementó programación concurrente.Específicamente, ThreadPoolExecutor se empleó para extraer de manera eficiente la información individual de cada película mediante múltiples solicitudes web simultáneas, mientras que multiprocessing.Pool permitió ejecutar en paralelo ambos filtros (ascendente ```?sort=rank%2Cdesc```y descendente ```?sort=rank%2Casc```) para obtener los datos de las páginas de forma concurrente, maximizando así la eficiencia del proceso de scraping.

# Preguntas adicionales:

1. Cómo configurarías Selenium o Playwright para acceder a las páginas de
IMDB (en términos de configuración de navegador, manejo de headers,
cookies, etc.):

✅ Utilizar Undetected-Chromedriver (evita la detección de Selenium).
✅ ```WebDriverWait(driver, time:int)``` Para simular el comportamiento humano
✅ Anadir argumentos como ```
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_argument("--headless=new")  # Optional: Run in headless mode```


2. Cómo navegarías entre las páginas de IMDB para obtener el listado de películas y acceder a la página de detalle de cada una.

✅ Para obtener todas las peliculas es necesario realizar un "scroll down" para ello se ejecuta una secuencia de Javascript para realizarlo con ```driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")```   

✅ Es necesario esperar que todo el DOM cargue se puede hacer con un ```WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return document.body.scrollHeight") > last_height
        )```

3. Cómo extraerías los datos de cada página (título, año, calificación,
duración, metascore, elenco) utilizando estas tecnologías.

✅ Con el WebDriver se obtiene el ```driver.page_source``` y se pueden utilizar las mismas funciones hechas en este ejercicio para obtener la data con ```BeautifulSoup(driver.page_source, 'html.parser')```

![alt text](image-1.png) __Imagen 1__

✅ Con el estilo de vista mostrado en la imagen se puede obtener bastante información sin necesidad de entrar a cada página del detalle, esto mejora considerablemente la eficiencia del script, se puede realizar con un:
```
button = driver.find_element(By.ID, "list-view-option-detailed")
driver.execute_script("arguments[0].click();", button)
```

✅ Al igual que en el ejercicio anterior, donde se implementó un sistema para acceder a cada página de detalles mediante los enlaces href utilizando programación concurrente, es posible aplicar la misma configuración del driver de Selenium para navegar eficientemente a las páginas individuales de cada película.

4. Cómo manejarías el tiempo de espera entre solicitudes (esperas explícitas
o implícitas) para evitar bloqueos y errores.

✅ Para manejar correctamente el scroll y contenido dinámico, se recomienda implementar "Explicit Waits" (esperas explícitas) que verifiquen activamente la carga del contenido o la finalización del scroll automático. Se puede usar lo siguente ```WebDriverWait(driver, 15).until(
    lambda d: d.execute_script("return (window.scrollY + window.innerHeight) >= document.body.scrollHeight")
)```

5. Cómo manejarías los posibles problemas que puedan surgir al utilizar
estas tecnologías (por ejemplo, bloquear IP, captchas, JavaScript cargado
dinámicamente).

✅ Para manejar los bloqueos de IP, Proxies rotativos (SmartProxy) o Plataformas pagas proveedoras de proxies, librerias como ```random_user_agent``` para obtener distintos user agents

✅ Usar presolved Captcha, o librerias como TwoCaptcha (Paga)

✅ Utilizar Explicit Waits


# IMPORTANTE

* En la carpeta ```results``` estan los excel con los datos obtenidos de la DB ya cargada
* El nombre de la db es result.db esta en SQLite3
