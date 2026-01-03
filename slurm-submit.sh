#!/bin/bash

# ./slurm-submit <os-image|all|all_cpu|all_gpu> <command|all>
# ./slurm-submit debian-11 image
# ./slurm-submit debian-11 clone [afterjobid]

image="$1"
action="$2"
afterjobid="$3"

if [ -z "$image" ]; then
    echo "Error: no image given"
    exit 1
fi

if [ -z "$action" ]; then
    echo "Error: no command given"
    exit 1
fi

export image
export action

function submit
{
    jobid=""
    tmpf=$(mktemp)
    envsubst < slurm-template-container.sh > $tmpf
    if [ -z "$afterjobid" ]; then
      #echo "submit $image $action"
       jobid=$(sbatch $tmpf | awk '{print $4}')
    else
      #echo "submit $image $action (depend on $afterjobid)"
       jobid=$(sbatch -d afterok:$afterjobid $tmpf | awk '{print $4}')
    fi
    echo $jobid
    /bin/rm $tmpf
}

function build_image
{
    jobid=""
    tmpf=$(mktemp)
    envsubst < slurm-template-image.sh > $tmpf
    echo "submit $image $action"
    sbatch $tmpf
    /bin/rm $tmpf
}

function do_action
{
  action=$1
  case "$action" in
    ( "clone" | "update" | "clean" | "cmake" )
      export ntasks=1
      export ncores=2
      export ngpus=0
      submit
      ;;
    ( "build" )
      export ntasks=1
      export ncores=8
      export ngpus=0
      submit
      ;;
    ( "test.serial" )
      export ntasks=1
      export ncores=1
      export ngpus=0
      submit
      ;;
    ( "test.openmp" )
      export ntasks=1
      export ncores=4
      export ngpus=0
      submit
      ;;
    ( "test.parallel" )
      export ntasks=1
      export ncores=4
      export ngpus=0
      submit
      ;;
    ( "test.cuda.serial" )
      export ntasks=1
      export ncores=1
      export ngpus=1
      submit
      ;;
    ( "image" )
      export ntasks=1
      export ncores=8
      export ngpus=0
      build_image
      ;;
    ( "all" )
      export afterjobid=""
      for i in clone clean cmake build test.openmp test.serial
      do
          afterjobid=$(do_action $i)
      done
      ;;
  esac
}

case "$image" in
  ( "all" )
    for image in $(make cpuimages)
    do
        export ngpus=0
        echo $image
        do_action $action
    done
    for image in $(make gpuimages)
    do
        export ngpus=1
        echo $image
        do_action $action
    done
    ;;
  ( "all_cpu" )
    for image in $(make cpuimages)
    do
        export ngpus=0
        echo $image
        do_action $action
    done
    ;;
  ( "all_gpu" )
    for image in $(make gpuimages)
    do
        export ngpus=1
        echo $image
        do_action $action
    done
    ;;
  ( * )
    do_action $action
    ;;
esac
