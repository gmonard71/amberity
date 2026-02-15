#!/bin/bash

#SBATCH -p std
#SBATCH -N 1
#SBATCH -n ${ntasks}
#SBATCH -c ${ncores}
#SBATCH --gres=gpu:${ngpus}
#SBATCH -J ${action}-${image}
#SBATCH -o logs/slurm/${image}-${action}
#SBATCH -e logs/slurm/${image}-${action}

echo "Running on: " $(hostname)
echo "Image: "${image}
pwd

if [ -e /dev/nvidia0 ]; then
nvidia-smi
fi

echo "Starting: $(date +%F/%T)"
mkdir -p logs/${image}
./amberity -l logs/${image}/${action} --singularity container ${image} ${action} ${args}
echo "Finished: $(date +%F/%T)"
sleep 2
