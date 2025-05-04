import time
from scraper import multiprocess_manage
from logger_ import logger
    
if __name__ == "__main__":
    try:
        sorts = ["?sort=rank%2Cdesc", "?sort=rank%2Casc"]
        start_time = time.time()
        
        logger.info("Start app...")
        logger.info("Start IMDB Extract Movies...")
        
        multiprocess_manage(sorts=sorts)
        
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info("Finish the page IMDB Top Movies... ")
        logger.warning(f"Execution time {round(execution_time)}")
        
    except Exception as e:
        logger.error(str(e))
        logger.fatal("Stop execution...")
    
    