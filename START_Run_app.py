import os
import sys
from streamlit.web import cli as stcli

port=8515

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    # Config Streamlit com tema dark
    os.environ['STREAMLIT_SERVER_PORT'] = f'{port}'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_THEME_BASE'] = 'dark'

    # Caminho do APP_.py
    app_path = resource_path('APP_.py')

    sys.argv = [
        'streamlit', 'run', app_path, 
        f'--server.port={port}',
        '--server.headless=true',
        '--theme.base=dark',
        '--global.developmentMode=false'
    ]

    stcli.main()
