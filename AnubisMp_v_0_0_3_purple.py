import asyncio
import json
import ssl
import time
import urllib.error
import urllib.request
import webbrowser
from nicegui import ui
import yt_dlp

try:
    import certifi
    _SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _SSL_CONTEXT = None

LOGO_DATA_URI = 'data:image/x-icon;base64,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'

_state = {'query': '', 'fetched': 0, 'batch': 20}
_pstate = {
    'current_id': None,
    'current_title': '',
    'current_channel': '',
    'current_thumb': '',
    'current_video': None,
    'loaded': False,
    'playing': False,
}

_active_row: dict = {'btn': None, 'row': None}

_queue: list = []

_history: list = []

_seek_state = {'last_change': 0.0}

_preload_state = {'video_id': None, 'url': None}
PRELOAD_LEAD_SECONDS = 5.0

APP_VERSION = 'v0.0.3'

GITHUB_REPO = 'emistar1/Anubis_MP'

_play_gen = {'value': 0}
_search_gen = {'value': 0}

_search_cache = {'query': None, 'entries': []}

_volume_state = {'value': 100}


def _parse_version(v: str) -> tuple[int, ...]:
    v = v.strip().lstrip('vV')
    parts = []
    for chunk in v.split('.'):
        digits = ''
        for ch in chunk:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _fetch_latest_release() -> dict | None:
    if not GITHUB_REPO or GITHUB_REPO == 'your-username/your-repo':
        print('[update-check] GITHUB_REPO is not configured, skipping.')
        return None
    headers = {'Accept': 'application/vnd.github+json'}

    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CONTEXT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            print(f'[update-check] GitHub API error {exc.code}: {exc.reason}')
            return None
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f'[update-check] request to {url} failed: {exc}')
        return None

    list_url = f'https://api.github.com/repos/{GITHUB_REPO}/releases'
    try:
        req = urllib.request.Request(list_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=_SSL_CONTEXT) as resp:
            releases = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
        print(f'[update-check] request to {list_url} failed: {exc}')
        return None
    if not releases:
        print('[update-check] repo has no releases/tags published yet.')
        return None
    return releases[0]


async def _check_for_updates() -> None:
    release = await asyncio.to_thread(_fetch_latest_release)
    if not release:
        return
    latest_tag = release.get('tag_name') or ''
    if not latest_tag:
        print('[update-check] latest release has no tag_name.')
        return
    print(f'[update-check] local={APP_VERSION!r} latest={latest_tag!r}')
    if _parse_version(latest_tag) <= _parse_version(APP_VERSION):
        return
    release_url = release.get('html_url') or f'https://github.com/{GITHUB_REPO}/releases'
    notes = (release.get('body') or '').strip()
    with ui.dialog() as _update_dialog, ui.card().style(
        'background:#181818;min-width:320px;max-width:420px;padding:20px;'
    ):
        ui.label(f'Update available: {latest_tag}').style(
            'color:#fff;font-size:16px;font-weight:700;'
        )
        ui.label(f"You're on v{APP_VERSION}.").style('color:#a7a7a7;font-size:13px;')
        if notes:
            ui.label(notes[:280]).style(
                'color:#ccc;font-size:12px;white-space:pre-wrap;margin-top:8px;'
            )
        with ui.row().style('justify-content:flex-end;gap:8px;margin-top:16px;'):
            ui.button('Later', on_click=_update_dialog.close).props('flat').style(
                'color:#a7a7a7;'
            )
            ui.button(
                'Download', on_click=lambda: webbrowser.open(release_url)
            ).style('background:#a4133c;color:#fff;')
    _update_dialog.open()


def _fmt_views(n: int | None) -> str:
    if not n:
        return ''
    if n >= 1_000_000:
        return f'{n / 1_000_000:.1f}M plays'
    if n >= 1_000:
        return f'{n / 1_000:.0f}K plays'
    return f'{n:,} plays'


def _fmt_dur(secs: int | None) -> str:
    if not secs:
        return ''
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f'{h}:{m:02}:{s:02}' if h else f'{m}:{s:02}'


def _best_thumb(video: dict) -> str:
    for t in reversed(video.get('thumbnails') or []):
        if t.get('url'):
            return t['url']
    vid_id = video.get('id', '')
    return f'https://img.youtube.com/vi/{vid_id}/mqdefault.jpg'


def _yt_fetch(query: str, start: int, count: int) -> list[dict]:
    need = start + count
    if _search_cache['query'] == query and len(_search_cache['entries']) >= need:
        return _search_cache['entries'][start:start + count]
    opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f'ytsearch{need}:{query}', download=False)
    entries = info.get('entries') or []
    _search_cache['query'] = query
    _search_cache['entries'] = entries
    return entries[start:start + count]


def _get_audio_url(video_url: str) -> str:
    opts = {'format': 'bestaudio', 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info['url']


def _reset_row_icon() -> None:
    btn = _active_row['btn']
    row = _active_row['row']
    if btn is not None:
        btn.props('icon=play_arrow')
    if row is not None:
        row.classes(remove='row-active row-playing')
    _active_row['btn'] = None
    _active_row['row'] = None


def _set_row_playing(btn=None, row=None) -> None:
    _reset_row_icon()
    if btn is not None:
        btn.props('icon=pause')
        _active_row['btn'] = btn
    if row is not None:
        row.classes(add='row-active row-playing')
        _active_row['row'] = row


def _pause() -> None:
    audio_player.pause()
    _pstate['playing'] = False
    _player_btn.props('icon=play_arrow')
    if _active_row['btn'] is not None:
        _active_row['btn'].props('icon=play_arrow')
    if _active_row['row'] is not None:
        _active_row['row'].classes(remove='row-playing')


def _resume() -> None:
    audio_player.play()
    _pstate['playing'] = True
    _player_btn.props('icon=pause')
    if _active_row['btn'] is not None:
        _active_row['btn'].props('icon=pause')
    if _active_row['row'] is not None:
        _active_row['row'].classes(add='row-playing')


def _player_toggle() -> None:
    if not _pstate['loaded']:
        return
    if _pstate['playing']:
        _pause()
    else:
        _resume()


async def _preload_next_track() -> None:
    if not _queue:
        return
    nxt = _queue[0]
    vid_id = nxt.get('id', '')
    if not vid_id or _preload_state['video_id'] == vid_id:
        return
    _preload_state['video_id'] = vid_id
    _preload_state['url'] = None
    url = f'https://www.youtube.com/watch?v={vid_id}'
    try:
        audio_url = await asyncio.to_thread(_get_audio_url, url)
    except Exception:
        if _preload_state['video_id'] == vid_id:
            _preload_state['video_id'] = None
        return
    if _preload_state['video_id'] == vid_id:
        _preload_state['url'] = audio_url


async def _wait_for_buffer(min_seconds: float = 10.0, timeout: float = 12.0) -> None:
    js = (
        "return await new Promise((resolve) => {"
        "  const a = document.getElementById('audio-player');"
        "  if (!a) { resolve(false); return; }"
        f"  const deadline = Date.now() + {timeout * 1000};"
        "  function check() {"
        "    const buf = a.buffered;"
        "    const ahead = buf.length ? buf.end(buf.length - 1) - a.currentTime : 0;"
        f"    if (ahead >= {min_seconds} || a.readyState >= 4 || Date.now() > deadline) {{"
        "      resolve(true);"
        "    } else {"
        "      setTimeout(check, 150);"
        "    }"
        "  }"
        "  check();"
        "});"
    )
    try:
        await ui.run_javascript(js, timeout=timeout + 2)
    except Exception:
        pass


async def _play_track(video: dict, row_btn=None, row_el=None) -> None:
    vid_id = video.get('id', '')
    url = f'https://www.youtube.com/watch?v={vid_id}'
    title = video.get('title') or 'Untitled'
    channel = video.get('channel') or video.get('uploader') or 'Unknown'
    thumb = _best_thumb(video)

    if _pstate['current_id'] == vid_id and _pstate['loaded']:
        _player_toggle()
        return

    _play_gen['value'] += 1
    my_gen = _play_gen['value']

    prev_id = _pstate['current_id']
    prev_title = _pstate['current_title']
    prev_channel = _pstate['current_channel']
    prev_thumb = _pstate['current_thumb']
    prev_video = _pstate['current_video']
    prev_loaded = _pstate['loaded']
    prev_playing = _pstate['playing']

    _player_thumb.set_source(thumb)
    _player_title.set_text(title)
    _player_channel.set_text(channel)
    _player_btn.props('icon=hourglass_empty')
    _player_btn.disable()
    _progress_slider._props['model-value'] = 0
    _progress_slider.update()
    _time_current.set_text('0:00')
    _time_total.set_text('0:00')
    if row_btn is not None:
        row_btn.props('icon=hourglass_empty')

    if _preload_state['video_id'] == vid_id and _preload_state['url']:
        audio_url = _preload_state['url']
    else:
        try:
            audio_url = await asyncio.to_thread(_get_audio_url, url)
        except Exception as exc:
            if my_gen != _play_gen['value']:
                return
            ui.notify(f'Playback failed: {exc}', color='negative', position='bottom-right')
            if row_btn is not None:
                row_btn.props('icon=play_arrow')
            if prev_video is not None:
                _pstate['current_id'] = prev_id
                _pstate['current_title'] = prev_title
                _pstate['current_channel'] = prev_channel
                _pstate['current_thumb'] = prev_thumb
                _pstate['current_video'] = prev_video
                _pstate['loaded'] = prev_loaded
                _pstate['playing'] = prev_playing
                _player_thumb.set_source(prev_thumb)
                _player_title.set_text(prev_title)
                _player_channel.set_text(prev_channel)
                _player_btn.props('icon=pause' if prev_playing else 'icon=play_arrow')
            else:
                _pstate['current_id'] = None
                _pstate['loaded'] = False
                _pstate['playing'] = False
                _player_thumb.set_source('')
                _player_title.set_text('No track selected')
                _player_channel.set_text('Search and pick a song')
                _player_btn.props('icon=play_arrow')
            _player_btn.enable()
            return

    if my_gen != _play_gen['value']:
        return

    if _preload_state['video_id'] == vid_id:
        _preload_state['video_id'] = None
        _preload_state['url'] = None
    audio_player.set_source(audio_url)
    audio_player.update()
    await _wait_for_buffer()

    if my_gen != _play_gen['value']:
        return

    audio_player.play()
    _pstate['loaded'] = True
    _pstate['playing'] = True
    _pstate['current_id'] = vid_id
    _pstate['current_title'] = title
    _pstate['current_channel'] = channel
    _pstate['current_thumb'] = thumb
    _pstate['current_video'] = video
    _player_btn.props('icon=pause')
    _player_btn.enable()
    _set_row_playing(row_btn, row_el)


async def _on_audio_error(e=None) -> None:
    if not _pstate['current_id'] or not _pstate['loaded']:
        return
    ui.notify('Playback error — the stream may have expired.', color='negative',
              position='bottom-right')
    _pause()


def _add_to_queue(video: dict) -> None:
    _queue.append(video)
    ui.notify(f'Added "{video.get("title") or "Untitled"}" to queue',
              position='bottom-right')
    _queue_list_ui.refresh()


def _remove_from_queue(idx: int) -> None:
    if 0 <= idx < len(_queue):
        _queue.pop(idx)
    _queue_list_ui.refresh()


def _move_in_queue(idx: int, direction: int) -> None:
    new_idx = idx + direction
    if 0 <= idx < len(_queue) and 0 <= new_idx < len(_queue):
        _queue[idx], _queue[new_idx] = _queue[new_idx], _queue[idx]
    _queue_list_ui.refresh()


async def _play_next_in_queue() -> None:
    if _pstate['current_video'] is not None:
        _history.append(_pstate['current_video'])
    if not _queue:
        _pstate['playing'] = False
        _player_btn.props('icon=play_arrow')
        _reset_row_icon()
        return
    next_video = _queue.pop(0)
    _queue_list_ui.refresh()
    await _play_track(next_video)


async def _on_track_ended(e=None) -> None:
    await _play_next_in_queue()


async def _skip_forward() -> None:
    if not _queue:
        ui.notify('Queue is empty', position='bottom-right')
        return
    if _pstate['current_video'] is not None:
        _history.append(_pstate['current_video'])
    next_video = _queue.pop(0)
    _queue_list_ui.refresh()
    await _play_track(next_video)


async def _skip_backward() -> None:
    if not _history:
        ui.notify('No previous track', position='bottom-right')
        return
    prev_video = _history.pop()
    if _pstate['current_video'] is not None:
        _queue.insert(0, _pstate['current_video'])
        _queue_list_ui.refresh()
    await _play_track(prev_video)


async def _paint_progress(played_pct: float | None = None):
    override = 'null' if played_pct is None else played_pct
    js = (
        "const a = document.getElementById('audio-player');"
        "if (!a) return [0, 0];"
        "const dur = a.duration || 0;"
        "const cur = a.currentTime || 0;"
        "let bufEnd = 0;"
        "if (a.buffered && a.buffered.length) {"
        "  bufEnd = a.buffered.end(a.buffered.length - 1);"
        "}"
        "if (dur > 0) {"
        f"  const override = {override};"
        "  const playedPct = override !== null ? override : Math.min(100, Math.max(0, (cur / dur) * 100));"
        "  const bufferedPct = Math.min(100, Math.max(0, (bufEnd / dur) * 100));"
        "  const track = document.querySelector('#progress-slider .q-slider__track');"
        "  if (track) {"
        "    track.style.background = 'linear-gradient(to right,'"
        "      + '#1ed760 0%, #a4133c ' + playedPct + '%,'"
        "      + 'rgba(255,255,255,0.5) ' + playedPct + '%, rgba(255,255,255,0.5) ' + bufferedPct + '%,'"
        "      + '#4d4d4d ' + bufferedPct + '%, #4d4d4d 100%)';"
        "  }"
        "}"
        "return [cur, dur];"
    )
    try:
        result = await ui.run_javascript(js)
    except Exception:
        return None
    return tuple(result) if result else None


async def _update_progress() -> None:
    if not _pstate['loaded']:
        return
    if time.monotonic() - _seek_state['last_change'] < 1.0:
        return
    result = await _paint_progress()
    if not result:
        return
    cur, dur = result
    if dur and dur > 0:
        _progress_slider._props['model-value'] = (cur / dur) * 100
        _progress_slider.update()
        _time_current.set_text(_fmt_dur(int(cur)))
        _time_total.set_text(_fmt_dur(int(dur)))
        if _queue and (dur - cur) <= PRELOAD_LEAD_SECONDS:
            asyncio.create_task(_preload_next_track())


async def _seek_to(pct: float) -> None:
    try:
        result = await ui.run_javascript(
            "const a = document.getElementById('audio-player');"
            "if (!a) return 'no-element';"
            "if (!a.duration) return 'no-duration';"
            f"a.currentTime = ({pct} / 100) * a.duration;"
            "return a.duration;"
        )
    except Exception as exc:
        ui.notify(f'Seek failed: {exc}', color='negative',
                   position='bottom-right')
        return
    if not isinstance(result, (int, float)):
        return
    dur = result
    _progress_slider._props['model-value'] = pct
    _progress_slider.update()
    _time_current.set_text(_fmt_dur(int((pct / 100) * dur)))
    await _paint_progress(played_pct=pct)


async def _on_slider_change(e) -> None:
    if e.value is None:
        return
    _seek_state['last_change'] = time.monotonic()
    await _seek_to(e.value)


async def _on_volume_change(e) -> None:
    if e.value is None:
        return
    _volume_state['value'] = e.value
    await ui.run_javascript(
        "const a = document.getElementById('audio-player');"
        f"if (a) a.volume = {e.value} / 100;"
    )


@ui.refreshable
def _queue_list_ui() -> None:
    if not _queue:
        with ui.column().classes('items-center w-full').style('padding:24px 4px;gap:6px;'):
            ui.icon('queue_music').style('color:#a7a7a7;font-size:28px;')
            ui.label('Queue is empty').style('color:#a7a7a7;font-size:13px;')
        return
    for i, v in enumerate(_queue):
        with ui.row().style(
            'align-items:center;gap:10px;width:100%;padding:6px 4px;'
        ):
            ui.image(_best_thumb(v)).style(
                'width:40px;height:40px;object-fit:cover;'
                'border-radius:4px;flex-shrink:0;'
            )
            with ui.column().style('gap:0;min-width:0;flex:1;'):
                ui.label(v.get('title') or 'Untitled').style(
                    'color:#fff;font-size:13px;white-space:nowrap;'
                    'overflow:hidden;text-overflow:ellipsis;max-width:220px;'
                )
                ui.label(v.get('channel') or v.get('uploader') or 'Unknown').style(
                    'color:#a7a7a7;font-size:11px;white-space:nowrap;'
                    'overflow:hidden;text-overflow:ellipsis;max-width:220px;'
                )
            with ui.column().style('gap:0;flex-shrink:0;'):
                ui.button(
                    icon='keyboard_arrow_up',
                    on_click=lambda e, idx=i: _move_in_queue(idx, -1)
                ).props('round dense flat').classes('queue-reorder-btn').style(
                    'color:#a7a7a7;width:24px;height:20px;min-width:24px;'
                ).set_enabled(i > 0)
                ui.button(
                    icon='keyboard_arrow_down',
                    on_click=lambda e, idx=i: _move_in_queue(idx, 1)
                ).props('round dense flat').classes('queue-reorder-btn').style(
                    'color:#a7a7a7;width:24px;height:20px;min-width:24px;'
                ).set_enabled(i < len(_queue) - 1)
            ui.button(
                icon='close', on_click=lambda e, idx=i: _remove_from_queue(idx)
            ).props('round dense flat').classes('queue-reorder-btn').style('color:#a7a7a7;')


def _add_row(video: dict) -> None:
    vid_id = video.get('id', '')
    title = video.get('title') or 'Untitled'
    channel = video.get('channel') or video.get('uploader') or 'Unknown'
    views = _fmt_views(video.get('view_count'))
    dur = _fmt_dur(video.get('duration'))
    thumb = _best_thumb(video)
    with _results:
        with ui.row().classes('track-row').style(
            'width:100%;align-items:center;gap:14px;padding:8px 12px;'
            'border-radius:6px;margin:0;flex-wrap:nowrap;'
        ) as row_el:

            with ui.element('div').classes('track-thumb-wrap').style(
                'position:relative;flex-shrink:0;width:48px;height:48px;'
            ):
                ui.image(thumb).style(
                    'width:48px;height:48px;object-fit:cover;'
                    'border-radius:4px;display:block;'
                )
                with ui.element('div').classes('eq-bars'):
                    ui.element('span')
                    ui.element('span')
                    ui.element('span')
                row_btn = ui.button(icon='play_arrow').props('round dense flat').classes(
                    'row-play-btn'
                ).style(
                    'position:absolute;inset:0;margin:auto;width:30px;height:30px;'
                    'min-width:30px;background:#a4133c;color:#000;'
                    'opacity:0;transition:opacity .12s;'
                )

            with ui.column().classes('track-meta').style('gap:1px;min-width:0;flex:1;'):
                ui.label(title).style(
                    'color:#fff;font-size:14px;font-weight:500;'
                    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
                    'max-width:100%;'
                )
                ui.label(channel).style(
                    'color:#a7a7a7;font-size:12px;white-space:nowrap;'
                    'overflow:hidden;text-overflow:ellipsis;max-width:100%;'
                )
            if views:
                ui.label(views).classes('track-views').style(
                    'color:#a7a7a7;font-size:13px;flex-shrink:0;'
                    'min-width:80px;text-align:right;'
                )
            ui.label(dur).classes('track-duration').style(
                'color:#a7a7a7;font-size:13px;flex-shrink:0;'
                'min-width:48px;text-align:right;'
            )

            ui.button(
                icon='playlist_add', on_click=lambda e, v=video: _add_to_queue(v)
            ).props('round dense flat').classes('queue-add-btn').style(
                'color:#a7a7a7;flex-shrink:0;min-width:30px;'
                'width:30px;height:30px;'
            )

        row_btn.on_click(lambda e, v=video, b=row_btn, r=row_el: _play_track(v, b, r))


async def _search() -> None:
    q = _search_input.value.strip()
    if not q:
        return

    _search_gen['value'] += 1
    my_gen = _search_gen['value']

    _state['query'] = q
    _state['fetched'] = 0
    _results.clear()
    _active_row['btn'] = None
    _active_row['row'] = None
    _load_row.set_visibility(False)
    _search_btn.disable()
    with _results:
        ui.spinner(size='3em', color='#a4133c').style('display:block;margin:48px auto;')
    try:
        videos = await asyncio.to_thread(_yt_fetch, q, 0, _state['batch'])
    except Exception as exc:
        if my_gen != _search_gen['value']:
            return
        _results.clear()
        with _results:
            with ui.column().classes('items-center w-full').style('padding:48px 0;gap:8px;'):
                ui.icon('error_outline').style('color:#f55;font-size:32px;')
                ui.label(f'Search failed: {exc}').style('color:#f55;font-size:14px;')
        return
    finally:
        _search_btn.enable()
    if my_gen != _search_gen['value']:
        return
    _results.clear()
    if not videos:
        with _results:
            with ui.column().classes('items-center w-full').style('padding:48px 0;gap:8px;'):
                ui.icon('search_off').style('color:#a7a7a7;font-size:32px;')
                ui.label('No results found.').style('color:#a7a7a7;font-size:14px;')
        return
    for v in videos:
        _add_row(v)
    _state['fetched'] = len(videos)
    _load_row.set_visibility(bool(videos))


async def _load_more() -> None:
    q = _state['query']
    if not q:
        return
    my_gen = _search_gen['value']
    _load_btn.disable()
    _load_spinner.set_visibility(True)
    try:
        videos = await asyncio.to_thread(_yt_fetch, q, _state['fetched'], _state['batch'])
        if my_gen != _search_gen['value']:
            return
        for v in videos:
            _add_row(v)
        _state['fetched'] += len(videos)
    except Exception as exc:
        if my_gen == _search_gen['value']:
            ui.notify(f'Load failed: {exc}', color='negative', position='bottom-right')
    finally:
        if my_gen == _search_gen['value']:
            _load_btn.enable()
            _load_spinner.set_visibility(False)


ui.add_head_html('''
<style>
  body, .nicegui-content, .q-page {
    background: #000000 !important;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif !important;
  }
  .track-row:hover {
    background: #1a1a1a !important;
  }
  .track-row:hover .row-play-btn {
    opacity: 1 !important;
  }
  .row-play-btn:hover {
    transform: scale(1.06);
  }
  #progress-slider .q-slider__selection {
    background: transparent !important;
  }
  #progress-slider .q-slider__track {
    background: #4d4d4d;
  }
  .q-field--outlined .q-field__control {
    background: #1f1f1f !important;
    border-radius: 999px !important;
  }
  .q-field--outlined .q-field__control:before {
    border: none !important;
  }
  ::-webkit-scrollbar { width: 10px; }
  ::-webkit-scrollbar-track { background: #000; }
  ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 6px; }

  .q-btn .q-icon { transition: transform .15s ease, opacity .15s ease; }

  .load-more-btn:hover { color:#a4133c !important; border-color:#a4133c !important; }
  .transport-btn:hover { color:#a4133c !important; }
  .queue-add-btn:hover, .queue-reorder-btn:hover { color:#a4133c !important; }

  .track-row.row-active {
    background: #151515;
    border-left: 3px solid #a4133c;
    padding-left: 9px;
  }
  .track-row.row-active .row-play-btn { opacity: 0; }
  .track-row.row-active:hover .row-play-btn { opacity: 1 !important; }
  .track-row.row-active:hover .eq-bars { display: none; }
  .eq-bars {
    display: none;
    position: absolute;
    inset: 0;
    margin: auto;
    width: 16px;
    height: 14px;
    align-items: flex-end;
    justify-content: center;
    gap: 2px;
    pointer-events: none;
    z-index: 1;
  }
  .track-row.row-active .eq-bars { display: flex; }
  .eq-bars span {
    display: block;
    width: 3px;
    background: #1ed760;
    border-radius: 1px;
    animation: eq-bounce 0.9s ease-in-out infinite;
    animation-play-state: paused;
  }
  .track-row.row-playing .eq-bars span { animation-play-state: running; }
  .eq-bars span:nth-child(1) { height: 40%; animation-delay: 0s; }
  .eq-bars span:nth-child(2) { height: 100%; animation-delay: .2s; }
  .eq-bars span:nth-child(3) { height: 65%; animation-delay: .4s; }
  @keyframes eq-bounce {
    0%, 100% { transform: scaleY(0.4); }
    50% { transform: scaleY(1); }
  }

  #scrub-tooltip { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; }

  .results-panel {
    background: #0a0a0a;
    box-shadow: 0 4px 24px rgba(0, 0, 0, .5);
  }

  @media (max-width: 560px) {
    .track-views { display: none !important; }
    .track-row { gap: 8px !important; padding: 8px 6px !important; }
    .track-meta { max-width: 100% !important; }
  }
</style>
<script>
(function () {
  function attach() {
    const slider = document.querySelector('#progress-slider');
    const audio = document.getElementById('audio-player');
    if (!slider || !audio) { setTimeout(attach, 300); return; }
    let tip = document.getElementById('scrub-tooltip');
    if (!tip) {
      tip = document.createElement('div');
      tip.id = 'scrub-tooltip';
      tip.style.cssText = 'position:fixed;pointer-events:none;background:#000;color:#fff;'
        + 'font-size:11px;padding:2px 6px;border-radius:4px;z-index:9999;display:none;'
        + 'transform:translate(-50%,-130%);white-space:nowrap;';
      document.body.appendChild(tip);
    }
    function fmt(s) {
      s = Math.max(0, Math.floor(s));
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      const sec = s % 60;
      const mm = h ? String(m).padStart(2, '0') : String(m);
      const ss = String(sec).padStart(2, '0');
      return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
    }
    slider.addEventListener('mousemove', function (ev) {
      const dur = audio.duration || 0;
      if (!dur) { tip.style.display = 'none'; return; }
      const rect = slider.getBoundingClientRect();
      const pct = Math.min(1, Math.max(0, (ev.clientX - rect.left) / rect.width));
      tip.textContent = fmt(pct * dur);
      tip.style.left = ev.clientX + 'px';
      tip.style.top = rect.top + 'px';
      tip.style.display = 'block';
    });
    slider.addEventListener('mouseleave', function () {
      tip.style.display = 'none';
    });
  }
  attach();
})();
</script>
''')

with ui.element('div').style(
    'position:sticky;top:0;z-index:200;width:100%;'
    'background:linear-gradient(180deg,#1a1a1a,#0f0f0f 90%);padding:16px 0;'
    'box-shadow:0 2px 14px rgba(0,0,0,.6);'
):
    with ui.row().classes('justify-center items-center w-full').style('gap:14px;'):
        ui.image(LOGO_DATA_URI).style('width:26px;height:26px;')
        ui.html(
            '<span style="color:#fff;font-size:19px;font-weight:800;'
            'letter-spacing:-.5px;margin-right:6px;">Anubis MP</span>'
        )
        _search_input = (
            ui.input(placeholder='What do you want to listen to?')
            .props('outlined rounded dense dark')
            .style('width:min(420px, 65vw);')
        )
        _search_input.on('keydown.enter', _search)
        _search_btn = ui.button('', icon='search', on_click=_search).style(
            'background:#a4133c;color:#000;border-radius:50%;'
            'min-width:38px;width:38px;height:38px;padding:0;'
        )

with ui.column().classes('items-center w-full').style(
    'background:#000000;min-height:100vh;padding:20px 12px 130px;'
):
    with ui.column().classes('items-center results-panel').style(
        'width:min(820px, 96vw);border-radius:12px;padding:12px;'
    ):
        _results = ui.column().style('width:100%;gap:2px;')
        _load_row = (
            ui.row()
            .classes('justify-center items-center')
            .style('width:100%;padding:18px 0 6px;')
        )
        with _load_row:
            _load_btn = ui.button(
                'Show more', on_click=_load_more, icon='expand_more'
            ).props('flat').classes('load-more-btn').style(
                'background:#181818;color:#fff;border:1px solid #2a2a2a;'
                'border-radius:500px;padding:8px 28px;font-size:13px;font-weight:600;'
            )
            _load_spinner = ui.spinner(size='1.2em', color='#a4133c').style('margin-left:10px;')
            _load_spinner.set_visibility(False)
        _load_row.set_visibility(False)

with ui.element('div').style(
    'position:fixed;bottom:0;left:0;width:100%;height:90px;z-index:300;'
    'background:#181818;border-top:1px solid #282828;'
    'display:flex;align-items:center;justify-content:space-between;'
    'padding:0 18px;box-sizing:border-box;'
):

    audio_player = ui.audio('').style('display:none;').props('id=audio-player preload=auto')

    audio_player.on('ended', _on_track_ended)
    audio_player.on('error', _on_audio_error)

    with ui.dialog() as _queue_dialog, ui.card().style(
        'background:#181818;min-width:320px;max-width:420px;'
        'max-height:70vh;padding:16px;'
    ):
        with ui.row().style(
            'justify-content:space-between;align-items:center;'
            'width:100%;margin-bottom:8px;'
        ):
            ui.label('Queue').style('color:#fff;font-size:16px;font-weight:700;')
            ui.button(icon='close', on_click=_queue_dialog.close).props(
                'round dense flat'
            ).style('color:#fff;')
        with ui.column().style(
            'width:100%;max-height:50vh;overflow-y:auto;gap:4px;'
        ):
            _queue_list_ui()

    with ui.row().style('align-items:center;gap:12px;width:30%;min-width:200px;'):
        _player_thumb = ui.image('').style(
            'width:56px;height:56px;border-radius:4px;object-fit:cover;'
            'background:#282828;flex-shrink:0;'
        )
        with ui.column().style('gap:0;min-width:0;'):
            _player_title = ui.label('No track selected').style(
                'color:#fff;font-size:13px;font-weight:500;white-space:nowrap;'
                'overflow:hidden;text-overflow:ellipsis;max-width:260px;'
            )
            _player_channel = ui.label('Search and pick a song').style(
                'color:#a7a7a7;font-size:11px;white-space:nowrap;'
                'overflow:hidden;text-overflow:ellipsis;max-width:260px;'
            )

    with ui.column().style('align-items:center;gap:4px;width:40%;max-width:520px;'):
        with ui.row().style('align-items:center;gap:16px;'):
            ui.button(icon='skip_previous', on_click=_skip_backward).props(
                'round flat'
            ).classes('transport-btn').style(
                'background:transparent;color:#fff;width:30px;height:30px;'
                'min-width:30px;padding:0;'
            )
            _player_btn = ui.button(
                icon='play_arrow', on_click=_player_toggle
            ).props('round').style(
                'background:#fff;color:#000;width:34px;height:34px;'
                'min-width:34px;padding:0;'
            )
            _player_btn.disable()
            ui.button(icon='skip_next', on_click=_skip_forward).props(
                'round flat'
            ).classes('transport-btn').style(
                'background:transparent;color:#fff;width:30px;height:30px;'
                'min-width:30px;padding:0;'
            )
            ui.button(icon='queue_music', on_click=_queue_dialog.open).props(
                'round flat'
            ).classes('transport-btn').style(
                'background:transparent;color:#fff;width:34px;height:34px;'
                'min-width:34px;padding:0;'
            )

        with ui.row().style('align-items:center;gap:8px;width:100%;'):
            _time_current = ui.label('0:00').style(
                'color:#a7a7a7;font-size:11px;min-width:34px;text-align:right;'
            )
            _progress_slider = ui.slider(
                min=0, max=100, step=0.1, value=0, on_change=_on_slider_change
            ).props(' dense id=progress-slider').style('flex:1;')
            _time_total = ui.label('0:00').style(
                'color:#a7a7a7;font-size:11px;min-width:34px;'
            )

    with ui.row().style(
        'align-items:center;gap:8px;width:30%;min-width:200px;justify-content:flex-end;'
    ):
        ui.icon('volume_up').style('color:#a7a7a7;font-size:20px;')
        _volume_slider = ui.slider(
            min=0, max=100, step=1, value=_volume_state['value'], on_change=_on_volume_change
        ).props('dense').style('width:100px;')

    ui.timer(1.0, _update_progress)
    ui.timer(2.0, _check_for_updates, once=True)

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='Anubis MP',
        dark=True,
        native=True,
        port=8000,
        favicon=LOGO_DATA_URI,
        reload=False,
    )
