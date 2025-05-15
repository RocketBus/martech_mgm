from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from app.src.scheduler import main

class ActionScheduler:
    """
    Classe responsável por agendar e executar tarefas assíncronas usando APScheduler
    com o scheduler baseado em asyncio.
    """
    
    def __init__(self):
        """
        Inicializa o scheduler assíncrono.
        """
        self.bk_sched_action = AsyncIOScheduler()

    def activate(self):
        """
        Inicia o scheduler, permitindo o agendamento e execução das tarefas.
        Deve ser chamado uma única vez durante o ciclo de vida da aplicação.
        """
        self.bk_sched_action.start()

    async def addJob(self, functionName: str, argument: dict, seconds: int = 1):
        """
        Agenda uma função assíncrona para ser executada após um tempo definido.

        Parâmetros:
        - functionName (str): Nome da função presente no módulo `main` a ser agendada.
        - argument (dict): Dicionário com os argumentos nomeados (`kwargs`) da função.
        - seconds (int, opcional): Quantos segundos a partir do momento atual a função deve ser executada. Default: 1 segundo.

        Exemplo de uso:
            await scheduler.addJob("process_order", {"order_id": 123}, seconds=5)
        """
        # Obtém a função real do módulo main dinamicamente
        realFunction = getattr(main, functionName, None)
        
        if not realFunction:
            raise AttributeError(f"Função '{functionName}' não encontrada no módulo 'main'.")

        # Agenda o job para execução única com atraso em segundos
        self.bk_sched_action.add_job(
            realFunction,
            trigger='date',
            run_date=datetime.now() + timedelta(seconds=seconds),
            kwargs=argument,
            name=f'run_action:{functionName}'
        )
