"""K-Width Tetris (3 players).

Rule:
    A row is cleared ONLY when *all* devices have completed the same row.

Networking:
    Uses the existing UDP Peer implementation from LAN/lan_connection.py.

Messages (UDP):
    - LINE-<row>               -> "I have row <row> full"
    - CLEAR-<row>-<clear_id>   -> Leader decided to clear row <row>

Notes:
    - This mode is fixed to exactly 3 players total (you + 2 peers).
    - To avoid double-clears (duplicates / UDP retries), only the leader
      (lowest IP address) emits CLEAR messages.
    - After any clear we reset tracking state, because row indices shift.
"""

from __future__ import annotations

import ipaddress
import sys
import threading
import time
from typing import Dict, Optional, Set, Tuple

import pygame as pg

from LAN import lan_connection as lan
from commons import button, colors
from tetris import game as g


REQUIRED_PLAYERS_TOTAL = 3  # you + 2 peers


class KWidthTetris(g.Game):
    def __init__(self, screen, bg_color, clock):
        super().__init__(screen, bg_color, clock)

        # Filled after lobby(): the 2 peers we actually play with.
        self.active_peers: list[str] = []
        self.players: Set[str] = set()
        self.leader_ip: Optional[str] = None

        # Row completion tracking
        self.reports_by_row: Dict[int, Set[str]] = {}
        self.local_full_rows: Set[int] = set()
        self.last_local_announce: Dict[int, float] = {}

        # Clear de-duplication
        self.seen_clears: Set[Tuple[int, int]] = set()  # (row, clear_id)

        # Game-over propagation / shutdown
        self._network_listen_thread: Optional[threading.Thread] = None
        self._remote_game_over: bool = False
        self._game_over_id_seen: Optional[int] = None

    # ----------------------------
    # Helpers
    # ----------------------------
    @staticmethod
    def _is_ready_true(val) -> bool:
        # known_peers may store bool or string
        return str(val) == "True"

    def _compute_leader(self) -> str:
        # Compare IPv4 addresses numerically (not lexicographically)
        leader = min(ipaddress.IPv4Address(ip) for ip in self.players)
        return str(leader)

    def _send_to_active_players(self, msg: str) -> None:
        for ip in self.active_peers:
            self.peer.send_msg_to_one_player(ip, msg)

    def _row_is_full(self, row: int) -> bool:
        # Grid cells are 0 for empty, non-zero for occupied
        return all(self.grid.grid[row][c] != 0 for c in range(self.grid.cols))

    def _clear_row(self, row: int) -> None:
        del self.grid.grid[row]
        self.grid.grid.insert(0, [0 for _ in range(self.grid.cols)])

    def _reset_kwidth_state(self) -> None:
        # Row indices shift after any clear, so we re-discover full rows
        self.reports_by_row.clear()
        self.local_full_rows.clear()
        self.last_local_announce.clear()


    def _broadcast_game_over(self) -> None:
        """Tell all active players that the game ended (someone lost)."""
        over_id = int(time.time() * 1000)
        # Send a few times for basic UDP reliability (no sleeps to avoid freezing the loop)
        for _ in range(3):
            self._send_to_active_players(f"GAMEOVER-{over_id}")

    def _stop_network_listening(self) -> None:
        """Stop UDP listen loop so we don't keep processing network after game end."""
        try:
            self.peer.stop_listen_event.set()
        except Exception:
            pass
        t = self._network_listen_thread
        if t and t.is_alive():
            t.join(timeout=2.0)

    # ----------------------------
    # Lobby (override) – require exactly 3 players
    # ----------------------------
    def lobby(self):
        self.peer = lan.Peer(self.gamemode)

        listening_thread = threading.Thread(target=self.peer.search_for_peers)
        broadcast_thread = threading.Thread(target=self.peer.broadcast)
        listening_thread.start()
        broadcast_thread.start()

        lobby_loop = True
        change_ready_status_button = button.Button(
            self.shift + 50,
            300,
            200,
            50,
            "Ready!",
            colors.color[8],
            colors.color[9],
            colors.color[0],
            self.peer.change_ready_status,
        )

        while lobby_loop:
            self.screen.fill(self.background_color)

            font = pg.font.Font(None, 32)
            title = font.render("K-Width (3 players)", True, colors.color[10])
            self.screen.blit(title, (self.shift + 55, 20))

            # Your status
            if self.peer.my_ready_status:
                change_ready_status_button.text = "Not ready"
                status = font.render("You: READY", True, colors.color[11])
            else:
                change_ready_status_button.text = "Ready!"
                status = font.render("You: NOT READY", True, colors.color[12])
            self.screen.blit(status, (self.shift + 70, 65))

            # Player count
            peers = list(self.peer.known_peers.keys())
            count = font.render(
                f"Players found: {1 + len(peers)}/{REQUIRED_PLAYERS_TOTAL}",
                True,
                colors.color[10],
            )
            self.screen.blit(count, (self.shift + 35, 110))

            # Peer readiness list
            small = pg.font.Font(None, 26)
            y = 150
            for ip in sorted(peers):
                rdy = self._is_ready_true(self.peer.known_peers[ip])
                txt = f"{ip} – {'READY' if rdy else 'NOT READY'}"
                self.screen.blit(small.render(txt, True, colors.color[10]), (self.shift + 30, y))
                y += 26

            # Start condition: exactly 2 peers, all ready, you ready
            ready_peers = sum(
                1 for ip in self.peer.known_peers if self._is_ready_true(self.peer.known_peers[ip])
            )
            enough_players = len(self.peer.known_peers) == (REQUIRED_PLAYERS_TOTAL - 1)
            all_ready = enough_players and (ready_peers == len(self.peer.known_peers))
            if all_ready and self.peer.my_ready_status is True:
                lobby_loop = False
                self.peer.stop_listen_event.set()
                self.peer.stop_broadcast_event.set()
                listening_thread.join()
                broadcast_thread.join()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.peer.quit()
                    self.peer.stop_listen_event.set()
                    self.peer.stop_broadcast_event.set()
                    listening_thread.join()
                    broadcast_thread.join()
                    pg.quit()
                    sys.exit()
                change_ready_status_button.handle_event(event)

            change_ready_status_button.draw(self.screen)
            pg.display.update()
            self.clock.tick(60)

        # Lock-in the 2 peers we are playing with
        self.active_peers = sorted(self.peer.known_peers.keys())[: (REQUIRED_PLAYERS_TOTAL - 1)]
        self.players = set(self.active_peers) | {self.peer.my_ip}
        self.leader_ip = self._compute_leader()

    # ----------------------------
    # K-Width logic
    # ----------------------------
    def _announce_local_full_rows(self) -> None:
        """Discover locally-full rows and announce them (with throttled retries)."""
        now = time.monotonic()

        for row in range(self.grid.rows - 1, -1, -1):
            if not self._row_is_full(row):
                continue

            if row not in self.local_full_rows:
                self.local_full_rows.add(row)
                self.reports_by_row.setdefault(row, set()).add(self.peer.my_ip)
                self.last_local_announce[row] = 0.0  # force immediate send

            last = self.last_local_announce.get(row, 0.0)
            if now - last >= 0.8:  # retry occasionally for UDP reliability
                self.reports_by_row.setdefault(row, set()).add(self.peer.my_ip)
                self._send_to_active_players(f"LINE-{row}")
                self.last_local_announce[row] = now

    def _handle_network_messages(self) -> None:
        while self.peer.received_msg:
            text, sender_ip = self.peer.received_msg.popleft()

            # Ignore non-active players if any slipped in
            if sender_ip not in self.players:
                continue

            if text.startswith("LINE-"):
                try:
                    row = int(text.split("-")[1])
                except (IndexError, ValueError):
                    continue
                if 0 <= row < self.grid.rows:
                    self.reports_by_row.setdefault(row, set()).add(sender_ip)

            elif text.startswith("GAMEOVER-"):
                # GAMEOVER-<id>
                try:
                    over_id = int(text.split("-")[1])
                except Exception:
                    over_id = None
                # Idempotent handling
                if over_id is None or over_id != self._game_over_id_seen:
                    self._game_over_id_seen = over_id
                    self._remote_game_over = True
                    self.loop = False

            elif text.startswith("CLEAR-"):
                # CLEAR-<row>-<clear_id>
                parts = text.split("-")
                if len(parts) != 3:
                    continue
                try:
                    row = int(parts[1])
                    clear_id = int(parts[2])
                except ValueError:
                    continue

                token = (row, clear_id)
                if token in self.seen_clears:
                    continue
                self.seen_clears.add(token)

                if 0 <= row < self.grid.rows:
                    self._clear_row(row)
                    self._reset_kwidth_state()

    def _leader_try_clear(self) -> None:
        """Leader checks for consensus and emits CLEAR."""
        if self.leader_ip != self.peer.my_ip:
            return

        eligible_rows = [
            row for row, reporters in self.reports_by_row.items() if reporters >= self.players
        ]
        if not eligible_rows:
            return

        # Clear the bottom-most eligible row first
        row = max(eligible_rows)
        clear_id = int(time.time() * 1000)

        # Broadcast the decision and clear locally once
        self._send_to_active_players(f"CLEAR-{row}-{clear_id}")
        self.seen_clears.add((row, clear_id))
        self._clear_row(row)
        self._reset_kwidth_state()


    def _draw_line_validations(self) -> None:
        """Draw plus markers at the left of the grid for each reported full row."""
        if not self.reports_by_row:
            return
        font = pg.font.Font(None, 28)
        x = self.grid.shift - 30  # left side of the grid
        for row, reporters in self.reports_by_row.items():
            if not reporters:
                continue
            count = len(reporters)
            # Draw one plus per player that validated that row
            txt = "+" * count
            y = row * self.grid.field_size + 4
            self.screen.blit(font.render(txt, True, colors.color[11]), (x, y))

    def draw(self):
        # Copy of base draw(), with additional validation markers.
        self.screen.fill(self.background_color)
        self.grid.draw(self.screen)

        self.current_block.draw(self.screen)

        tile_rect = pg.Rect(self.shift + 25 + 300, 75, 0.75 * self.shift, 125)
        pg.draw.rect(self.screen, colors.color[9], tile_rect)
        self.next_block.next_block_draw(self.screen)

        font = pg.font.Font(None, 36)
        text_surf = font.render("Next piece:", True, colors.color[10])
        self.screen.blit(text_surf, (self.shift + 35 + 300, 25))

        # K-Width addition: show how many players validated each full row
        self._draw_line_validations()

        pg.display.update()
        self.clock.tick(60)

    # ----------------------------
    # Game loop
    # ----------------------------
    def game_loop(self):
        self.peer.stop_listen_event.clear()
        listening_thread = threading.Thread(target=self.peer.listen, daemon=False)
        self._network_listen_thread = listening_thread
        listening_thread.start()

        block_goes_down = pg.USEREVENT + 1
        pg.time.set_timer(block_goes_down, 1000)

        clock_start = pg.time.get_ticks()
        game_time_sec = 0

        while self.loop:
            # 1) Local discovery + announcements
            self._announce_local_full_rows()

            # 2) Network receive
            self._handle_network_messages()

            # 3) Consensus clear (leader)
            self._leader_try_clear()

            # 4) Normal gameplay
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Treat window close as ending the game for everyone in this mode
                    try:
                        self._broadcast_game_over()
                    except Exception:
                        pass
                    self._stop_network_listening()
                    self.peer.quit()
                    pg.quit()
                    sys.exit()

                elif event.type == block_goes_down:
                    self.current_block.move_down(self.grid)
                    if self.current_block.check_collision_under(self.grid):
                        self.current_block.put_on_grid(self.grid)

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                        self.current_block.move_x(-1, self.grid)
                    elif event.key == pg.K_RIGHT:
                        self.current_block.move_x(1, self.grid)
                    elif event.key == pg.K_UP:
                        self.current_block.rotate(self.grid)
                    elif event.key == pg.K_DOWN:
                        self.current_block.move_down(self.grid)
                    elif event.key == pg.K_SPACE:
                        self.current_block.drop(self.grid)

            if self.current_block.is_placed:
                self.current_block = self.next_block
                if not self.current_block.check_collision_with_wall(0, self.grid):
                    self.next_block = self.random_new_block()
                else:
                    # Local loss -> end game for everyone
                    try:
                        self._broadcast_game_over()
                    except Exception:
                        pass
                    self.loop = False
                    clock_end = pg.time.get_ticks()
                    game_time_sec = (clock_end - clock_start) / 1000

            self.draw()

        # Stop network listening when the match is finished (local or remote game over)
        if game_time_sec == 0:
            clock_end = pg.time.get_ticks()
            game_time_sec = (clock_end - clock_start) / 1000
        self._stop_network_listening()
        self.game_over(self.screen, game_time_sec)


def start_k_width_game(screen, bg_color, clock):
    game = KWidthTetris(screen, bg_color, clock)
    game.gamemode = "K-Width"
    game.lobby()
    game.game_loop()
