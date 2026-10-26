# LOCAL ONLY: verify base image ID before build:
# sha256:6a88c34dc7da5bf5203f7debec4369734a46732830bdec652592d4cde1115121
# Same locked dependencies; only the explicitly opt-in browser traffic script differs.
# Context: capstone2/local-services/loadgen. No installation/network steps.
FROM capstone2-loadgen:local
COPY --chown=1000:1000 robot-shop.py /load/robot-shop.py
