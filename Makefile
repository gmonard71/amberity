
AMBERITY=amberity --singularity
CONFIG_YML=config.yml

IMAGES_ROOT=$(shell yq '.images_root' $(CONFIG_YML))
WORK_DIR=$(shell yq '.work_dir' $(CONFIG_YML))

#DRYRUN=echo
DRYRUN=

CPU_IMAGES=$(shell $(AMBERITY) image avail | grep -v cuda | grep -v gpu)
GPU_IMAGES=$(shell $(AMBERITY) image avail | egrep "cuda|gpu")
ALL_IMAGES=${CPU_IMAGES} ${GPU_IMAGES}

JSON_REPORTS=$(foreach NAME, ${ALL_IMAGES}, ${WORK_DIR}/${NAME}/report.json)

all:
	@echo "Please choose an action among:"
	@echo " - images                                   list all target images (cpu and gpu)"
	@echo " - cpuimages                                list all cpu target images"
	@echo " - gpuimages                                list all gpu target images"
	@echo " - list                                     list all defined images"
	@echo " - build                                    build all target images"
	@echo " - images/singularity/amber-<target>.sif    build a specific target image"
	@echo " - report                                   create json reports for all images"
	@echo " - wiki                                     create a wiki page to summarize all reports"
	@echo ""


images:
	@echo ${ALL_IMAGES}

cpuimages:
	@echo ${CPU_IMAGES}

gpuimages:
	@echo ${GPU_IMAGES}

list:
	$(AMBERITY) image list

# Build container images
build: $(foreach NAME, ${ALL_IMAGES}, ${IMAGES_ROOT}/singularity/amber-${NAME}.sif)

${IMAGES_ROOT}/singularity/amber-%.sif: os/%
	${DRYRUN} ${AMBERITY} image build $*

# create reports
report: $(JSON_REPORTS)

${WORK_DIR}/%/report.json:
	${DRYRUN} ${AMBERITY} container $* report

clean_report:
	/bin/rm -f $(JSON_REPORTS)

# create a wiki page reporting all results
wiki: report
	create_report_from_json.py --header reports/header.md --footer reports/footer.md $(JSON_REPORTS) > reports/wiki.md

