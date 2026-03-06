#!/bin/bash

#SBATCH -p std
#SBATCH -N 1
#SBATCH -n ${ntasks}
#SBATCH -c ${ncores}
#SBATCH -J imgbuild-${image}
#SBATCH -o logs/slurm/build-${image}
#SBATCH -e logs/slurm/build-${image}

echo "Running on: " $(hostname)
echo "Image: "${image}

echo "Starting: $(date +%F/%T)"
mkdir -p $(pwd)/logs/${image}
amberity -l $(pwd)/logs/${image}/${action} --singularity image build ${image}
echo "Finished: $(date +%F/%T)"
sleep 2
