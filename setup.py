from setuptools import setup
OPTIONS = {
    'iconfile': 'Anubis.icns',
    'argv_emulation': False,
    'packages': [
        'uvicorn',
        'nicegui',
        'fastapi',
        'starlette',
        'anyio',
        'anyio._backends',
        'yt_dlp',
    ],
    'includes': [
        'uvicorn.loops.asyncio',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan.on',
        'anyio._backends._asyncio',
    ],
}

setup(
    app=['AnubisMp.py'],
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)