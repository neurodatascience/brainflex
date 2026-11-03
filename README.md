# brainflex

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/neurodatascience/brainflex/main.svg)](https://results.pre-commit.ci/latest/github/neurodatascience/brainflex/main)

Brain federated learning experiment.

## Development

This project uses [uv](https://docs.astral.sh/uv/).

### Installation

```bash
uv sync
```

### Git hooks via `prek`

```bash
uv run prek install
uv run prek run -a
```

### Tests

```bash
uv run pytest
```

### Documentation

```bash
uv run make -C docs html
cd docs/_build/html
python -m http.server
```

### Docker images

- `vpn-client`: WireGuard VPN client
  ([`ghcr.io/neurodatascience/brainflex-vpn-client`](https://github.com/neurodatascience/brainflex/pkgs/container/brainflex-vpn-client))
- `vpn-server`: WireGuard VPN server, built on top of `vpn-client`
  ([`ghcr.io/neurodatascience/brainflex-vpn-server`](https://github.com/neurodatascience/brainflex/pkgs/container/brainflex-vpn-server))

To build locally:

```bash
docker build -t vpn-client docker/vpn-client
docker build -t vpn-server docker/vpn-server
```

Pushing a `docker/vX.Y.Z` tag builds both images and publishes them to GHCR with tags `X.Y.Z` and `latest`.

### Releases

CLI releases are tagged `cli/vX.Y.Z`.
Docker image releases are tagged `docker/vX.Y.Z`.

To create a release, tag the latest commit on the upstream `main` branch and push the tag upstream:

```bash
git fetch upstream

# Docker images
git tag -a docker/vX.Y.Z upstream/main -m "Docker images vX.Y.Z"
git push upstream docker/vX.Y.Z

# CLI
git tag -a cli/vX.Y.Z upstream/main -m "CLI vX.Y.Z"
git push upstream cli/vX.Y.Z
```

Tags must be on `main`: the Docker image workflow refuses to publish images for tags on other commits.
