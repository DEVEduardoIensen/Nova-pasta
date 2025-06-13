import logging

# Configurando logging pra gravar tudo num arquivo chamado neuroScalp.log
logging.basicConfig(filename='neuroScalp.log',
                    level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')

logging.info('Iniciando o bot...')