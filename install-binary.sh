#!/usr/bin/env sh

# Shamelessly copied from https://github.com/technosophos/helm-template
PROJECT_NAME="go-cqhttp"
PROJECT_GH="Mrs4s/go-cqhttp"
export GREP_COLOR="never"
# SHELL_FOLDER=$(cd "$(dirname "$0")";pwd)
PLUGIN_TMP_FILE="/tmp/${PROJECT_NAME}.tar.gz"
: ${VERSION="$1"}

# initArch discovers the architecture for this system.
initArch() {
  ARCH=$(uname -m)
  case $ARCH in
  armv5*) ARCH="armv5" ;;
  armv6*) ARCH="armv6" ;;
  armv7*) ARCH="armv7" ;;
  aarch64) ARCH="arm64" ;;
  x86) ARCH="386" ;;
  x86_64) ARCH="amd64" ;;
  i686) ARCH="386" ;;
  i386) ARCH="386" ;;
  esac
}

# initOS discovers the operating system for this system.
initOS() {
  OS=$(uname | tr '[:upper:]' '[:lower:]')

  case "$OS" in
  # Msys support
  msys*) OS='windows' ;;
  # Minimalist GNU for Windows
  mingw*) OS='windows' ;;
#   darwin) OS='darwin' ;;
  esac
}

# verifySupported checks that the os/arch combination is supported for
# binary builds.
verifySupported() {
  supported="linux-amd64\nlinux-arm\nlinux-386\ndarwin-amd64"
  if ! echo "${supported}" | grep -q "${OS}-${ARCH}"; then
    echo "No prebuild binary for ${OS}-${ARCH}."
    exit 1
  fi

  if ! type "curl" >/dev/null && ! type "wget" >/dev/null; then
    echo "Either curl or wget is required"
    exit 1
  fi
}

# getDownloadURL checks the latest available version.
getDownloadURL() {
  version=$VERSION
#   https://github.com/Mrs4s/go-cqhttp/releases/download/v0.9.38/go-cqhttp-v0.9.38-darwin-amd64.tar.gz
  if [ -n "$version" ]; then
    DOWNLOAD_URL="https://github.com/$PROJECT_GH/releases/download/$version/go-cqhttp-$version-${OS}-${ARCH}.tar.gz"
  else
    # Use the GitHub API to find the download url for this project.
    #    https://api.github.com/repos/Mrs4s/go-cqhttp/releases/latest
    #    https://api.github.com/repos/Mrs4s/go-cqhttp/releases
    url="https://api.github.com/repos/$PROJECT_GH/releases"
    if type "curl" >/dev/null; then
      # reponse=$(curl -s $url)
      DOWNLOAD_URLs=$(curl -s $url |grep ${OS}-${ARCH} |grep .tar.gz| awk '/\"browser_download_url\":/{gsub( /[,\"]/,"", $2); print $2}')
      DOWNLOAD_URL=`echo $DOWNLOAD_URLs|awk '{print $1}'`
    elif type "wget" >/dev/null; then
      DOWNLOAD_URLs=$(wget -q -O - $url  |grep ${OS}-${ARCH} |grep .tar.gz| awk '/\"browser_download_url\":/{gsub( /[,\"]/,"", $2); print $2}')
      DOWNLOAD_URL=`echo $DOWNLOAD_URLs|awk '{print $1}'`
    fi
  fi
}

# downloadFile downloads the latest binary package and also the checksum
# for that binary.
downloadFile() {
  echo "Downloading $DOWNLOAD_URL"
  if type "curl" >/dev/null; then
    curl -L "$DOWNLOAD_URL" -o "$PLUGIN_TMP_FILE"
  elif type "wget" >/dev/null; then
    wget -q -O "$PLUGIN_TMP_FILE" "$DOWNLOAD_URL"
  fi
}

# installFile verifies the SHA256 for the file, then unpacks and
# installs it.
installFile() {
  FILE_TMP="/tmp/$PROJECT_NAME"
  mkdir -p "$FILE_TMP"
  tar xf "$PLUGIN_TMP_FILE" -C "$FILE_TMP"
  FILE_TMP_BIN="$FILE_TMP/$PROJECT_NAME"
  echo "Preparing to install into ~"
  # mkdir -p "$SHELL_FOLDER/cqhttp"
  cp "$FILE_TMP_BIN" ~
}

# fail_trap is executed if an error occurs.
fail_trap() {
  result=$?
  if [ "$result" != "0" ]; then
    echo "Failed to install $PROJECT_NAME"
    printf '\tFor support, go to https://github.com/Mrs4s/go-cqhttp or 805104533@qq.com.\n'
  fi
  exit $result
}

# Execution

#Stop execution on any error
trap "fail_trap" EXIT
set -e
initArch
initOS
verifySupported
getDownloadURL
downloadFile
installFile
# testVersion

