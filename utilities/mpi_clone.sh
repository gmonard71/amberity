#!/bin/bash

yq=$(which yq)

if [ -z "$yq" ]; then
    echo "Error: please install yq to continue"
    exit 1
fi

openmpi_dir=$(cat config.yml | yq '.openmpi_dir')
work_dir=$(cat config.yml | yq '.work_dir')

ntasks=1
ncores=2
ngpus=0

for image in $(make cpuimages) $(make gpuimages)
do
    tmpf=$(mktemp)
    cat > $tmpf << END
#!/bin/bash

#SBATCH -p std
#SBATCH -N 1
#SBATCH -n ${ntasks}
#SBATCH -c ${ncores}
#SBATCH --gres=gpu:${ngpus}
#SBATCH -J mpi_clone-${image}
#SBATCH -o logs/slurm-${image}-mpi_clone
#SBATCH -e logs/slurm-${image}-mpi_clone

echo "Running on: " $(hostname)
echo "Image: "${image}
pwd

echo "Starting: $(date +%F/%T)"
rsync -av --delete \
  ${openmpi_dir} \
  ${work_dir}/${image}/.
echo "Finished: $(date +%F/%T)"
sleep 2
END
    echo "submit mpi_clone for $image"
    sbatch $tmpf
    /bin/rm $tmpf
done
