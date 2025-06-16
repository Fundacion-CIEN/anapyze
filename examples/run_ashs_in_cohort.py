import shutil
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor


COHORT_DIR = Path('/mnt/nasneuro_share/data/raws/PVallecas/niftis')
DERIVATIVES_RES_DIR = Path('/mnt/nasneuro_share/data/derivatives/ashs/PVallecas')
TEMP_BASE_DIR = Path('/mnt/WORK/data/ASHS_OUTPUT_TEMP')
ASHS_ROOT = '/mnt/WORK/software/ashs/bin/ashs_main.sh'
ATLAS_PATH = Path('/mnt/WORK/software/ashs/ashs_T1_atlas/ashsT1_atlas_upennpmc_07202018')
NUM_WORKERS = 8

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_visit(task_args):
    
    subj_id, visit_id, t1_image = task_args
    
    log = logging.getLogger(f"{subj_id}_{visit_id}")
    log.info(f"Starting process for {subj_id}")

    start_time_visit = datetime.now()
    
    temp_out_dir = TEMP_BASE_DIR / f"{subj_id}_{visit_id}"
    final_output_dir = DERIVATIVES_RES_DIR / subj_id / visit_id
    
    try:
        shutil.rmtree(temp_out_dir, ignore_errors=True)
        temp_out_dir.mkdir(parents=True, exist_ok=True)
        
        command = [
            ASHS_ROOT, '-I', f"{subj_id}_{visit_id}", '-a', str(ATLAS_PATH),
            '-g', str(t1_image), '-f', str(t1_image), '-w', str(temp_out_dir)
        ]
        
        # Usamos subprocess.run que es más seguro y robusto
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        shutil.rmtree(final_output_dir, ignore_errors=True)
        shutil.copytree(temp_out_dir, final_output_dir)
        shutil.rmtree(temp_out_dir)

        finish_time_visit = datetime.now()
        
        log.info(f"{subj_id} finished successfully.It took {finish_time_visit}")

        return f"{subj_id}/{visit_id}: Finished in {finish_time_visit}"

    except Exception as e:
        log.error(f"ERROR: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            log.error(f"Stderr: {e.stderr}")

        return f"{subj_id}/{visit_id}: Fallo"

def main():
    
    
    start_time = datetime.now()
    logging.info("Searching for jobs...")

    tasks = []

    for subj_path in COHORT_DIR.iterdir():
        if subj_path.is_dir():
            for visit_path in subj_path.iterdir():
                if visit_path.is_dir() and visit_path.name == 'V01': #OJO RESTRINGIMOS A VISITA 1
                    t1_image = visit_path / 'T1' / f'{subj_path.name}_T1_{visit_path.name}.nii.gz'
                    if t1_image.exists():
                        tasks.append((subj_path.name, visit_path.name, t1_image))

    logging.info(f"I found {len(tasks)} jobs!. Starting process with {NUM_WORKERS} images processed in parallel.")

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        results = executor.map(process_visit, tasks)

    # Imprimir resultados
    for result in results:
        logging.info(result)
        
    duration = datetime.now() - start_time
    logging.info(f"All tasks finished. Time: {duration}")

if __name__ == "__main__":
    main()