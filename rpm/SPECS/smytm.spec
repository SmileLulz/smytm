Name:    smytm
Version: 1.1.b2
Release: 1%{?dist}
Summary: CLI utility for searching and downloading music from YouTube and YouTube Music

License: GPL-3.0-only
URL:     https://github.com/SmileLulz/smytm
Source0: https://github.com/SmileLulz/smytm/archive/refs/tags/v%{version}.tar.gz

BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-hatchling
BuildRequires: appstream

Requires: python3-ytmusicapi
Requires: python3-mutagen
Requires: yt-dlp
Requires: ffmpeg-free
Requires: curl
Requires: chafa
Requires: AtomicParsley
Requires: rsgain

%generate_buildrequires
%pyproject_buildrequires

%description
smytm is a command-line utility for searching and downloading music and audio
from YouTube and YouTube Music. It uses yt-dlp and other external command-line
tools for searching, downloading, metadata processing, and terminal output.

%prep
%autosetup -n smytm-%{version}

%build
%pyproject_wheel

%install
%pyproject_install

install -Dm644 data/metainfo/io.github.SmileLulz.smytm.metainfo.xml \
    %{buildroot}%{_metainfodir}/io.github.SmileLulz.smytm.metainfo.xml

%check
appstreamcli validate \
    --no-net \
    %{buildroot}%{_metainfodir}/io.github.SmileLulz.smytm.metainfo.xml

%files
%doc WIKI.md
%license LICENSE

%{_bindir}/smytm
%{python3_sitelib}/smytm/
%{python3_sitelib}/smytm-*.dist-info/
%{_metainfodir}/io.github.SmileLulz.smytm.metainfo.xml

%changelog
* Wed Aug 26 2026 SmileLulz - 1.1.b2-1
- Version bump to 1.1.b2
- Testing Fedora build
