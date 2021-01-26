# Kubernetes centric workflow scheduler

Orchestrate running tasks on k8s on a schedule, the easy way.

**Status**: 🚧 Under construction 🚧


## Development

```
# build assets -- this requires you to have set
# SNOWPACK_PUBLIC_SOCKET_URL=ws://0.0.0.0:8000
npm run build

# run the scheduler
python -m lib.scheduler

# run the webserver at another prompt
python -m lib.app
```
