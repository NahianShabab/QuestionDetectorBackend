
import dotenv

def get_config()->dict:
    config = {
        **dotenv.dotenv_values('.secret_env'),
        **dotenv.dotenv_values('.shared_env')
    }
    return config