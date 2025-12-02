import random
import time
import sys

# Cross-platform curses support
try:
    import curses
except ImportError:
    # Windows fallback - try windows-curses package
    try:
        import windows_curses as curses
    except ImportError:
        print("Error: curses library not available.")
        print("On Windows, install with: pip install windows-curses")
        print("Or use Python 3.10+ which includes curses support.")
        sys.exit(1)

# Game constants
LANE_KEYS = ["a", "s", "d", "f"]
SPAWN_INTERVAL = 0.9
NOTE_SPEED = 0.22
HIT_WINDOW = 2
GAME_DURATION = 30
FEEDBACK_DURATION = 0.7
KEY_FEEDBACK_DURATION = 0.3
HIT_DISPLAY_TIME = 0.1

# Bar constants
BAR_DRAIN_RATE = 4.0
BAR_HIT_GAIN = 18.0
TRANSCENDING_HIT_GAIN = 13
TRANSCENDING_DRAIN_RATE = 0.5
POWER_UP_DURATION = 7.5
TRANSCEND_BONUS = 1000

# Color pairs
COLOR_HIT = 1
COLOR_MISS = 2
COLOR_FLASH_START = 3


class Note:
    def __init__(self, lane_idx, y):
        self.lane_idx = lane_idx
        self.y = y
        self.hit = False
        self.missed = False
        self.hit_time = None


def safe_addstr(stdscr, y, x, text, attr=0):
    """Safely add string with bounds checking"""
    try:
        max_y, max_x = stdscr.getmaxyx()
        if 0 <= y < max_y and 0 <= x < max_x:
            stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def safe_addch(stdscr, y, x, ch, attr=0):
    """Safely add character with bounds checking"""
    try:
        max_y, max_x = stdscr.getmaxyx()
        if 0 <= y < max_y and 0 <= x < max_x:
            stdscr.addch(y, x, ch, attr)
    except curses.error:
        pass


def get_flash_color(now):
    """Get current flash color for power-up effects"""
    flash_cycle = int((now * 5) % 3)
    return COLOR_FLASH_START + flash_cycle


def draw_bar_filled(stdscr, y, x, width, percent, flash_color, use_flash=False):
    """Draw a horizontal bar filled to the given percentage"""
    filled = int((percent / 100.0) * width)
    filled = min(filled, width)
    
    for i in range(filled):
        color = flash_color if (use_flash and percent >= 100.0) else COLOR_HIT
        safe_addch(stdscr, y, x + i, "█", curses.color_pair(color))


def draw_vertical_bar(stdscr, x, top, bottom, percent, flash_color, use_flash=False):
    """Draw a vertical bar filled to the given percentage"""
    height = bottom - top - 1
    filled = int((percent / 100.0) * height)
    filled = min(filled, height)
    
    for i in range(filled):
        y = bottom - i - 1
        if y > top:
            color = flash_color if (use_flash and percent >= 100.0) else COLOR_HIT
            safe_addch(stdscr, y, x + 1, "█", curses.color_pair(color))
            safe_addch(stdscr, y, x + 2, "█", curses.color_pair(color))


def show_instructions(stdscr):
    """Display game instructions and wait for player to start"""
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.clear()

    max_y, max_x = stdscr.getmaxyx()
    messages = [
        "Terminal Guitar Hero (Mini-Game)",
        "A S D F = guitar strings",
        "Notes fall down each lane with their key letter.",
        "Press the matching key (A/S/D/F) when the note crosses the '=' hit line.",
        "Hit close to the line for more points. Missing breaks your combo.",
        "Fill the score bar to 100% and press SPACE for a power-up!",
        "Controls: A S D F to play, SPACE for power-up, Q to quit.",
        "",
        "Press SPACE to start, or Q to quit."
    ]

    start_y = max_y // 2 - len(messages) // 2
    for i, msg in enumerate(messages):
        if msg:
            x = max_x // 2 - len(msg) // 2
            attr = curses.A_BOLD if i == 0 else (curses.A_BLINK if i == len(messages) - 1 else 0)
            safe_addstr(stdscr, start_y + i, x, msg, attr)
    
    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        if ch == ord(" "):
            return True
        if ch in (ord("q"), ord("Q")):
            return False


def draw_frame(stdscr, notes, score, combo, max_y, max_x, hit_row,
               feedback, feedback_type, last_hit_lane, last_miss_lane, 
               now, last_hit_time, last_miss_time, score_bar, 
               power_up_active, transcending_bar, waiting_for_transcend):
    """Draw the entire game frame"""
    stdscr.clear()
    
    # Constants for layout
    BAR_WIDTH = 3
    BAR_X = 1
    BAR_TOP = 4
    BAR_HEIGHT = max_y - BAR_TOP - 2
    BAR_BOTTOM = BAR_TOP + BAR_HEIGHT
    BAR_OFFSET = BAR_WIDTH + 2
    
    flash_color = get_flash_color(now) if (power_up_active or score_bar >= 100.0) else 0
    bar_full = score_bar >= 100.0
    
    # Draw transcending bar (horizontal, only during bonus mode)
    if power_up_active:
        TRANS_ROW = 3
        label = "TRANSCENDING:"
        label_x = BAR_OFFSET
        safe_addstr(stdscr, TRANS_ROW, label_x, label)
        
        bar_start_x = label_x + len(label) + 1
        bar_end_x = max_x - 2
        bar_width = bar_end_x - bar_start_x
        
        safe_addch(stdscr, TRANS_ROW, bar_start_x - 1, "[")
        safe_addch(stdscr, TRANS_ROW, bar_end_x, "]")
        
        use_flash = transcending_bar >= 100.0
        draw_bar_filled(stdscr, TRANS_ROW, bar_start_x, bar_width, 
                       transcending_bar, flash_color, use_flash)
    
    # Draw score bar (vertical)
    for y in range(BAR_TOP, BAR_BOTTOM + 1):
        safe_addch(stdscr, y, BAR_X, "|")
        safe_addch(stdscr, y, BAR_X + BAR_WIDTH - 1, "|")
    safe_addch(stdscr, BAR_TOP, BAR_X + 1, "-")
    safe_addch(stdscr, BAR_TOP, BAR_X + 2, "-")
    safe_addch(stdscr, BAR_BOTTOM, BAR_X + 1, "-")
    safe_addch(stdscr, BAR_BOTTOM, BAR_X + 2, "-")
    
    draw_vertical_bar(stdscr, BAR_X, BAR_TOP, BAR_BOTTOM, score_bar, 
                     flash_color, bar_full)

    # Title
    title = "Terminal Guitar Hero (A S D F)"
    title_x = max_x // 2 - len(title) // 2
    if power_up_active:
        safe_addstr(stdscr, 0, title_x, title, curses.color_pair(flash_color))
    else:
        safe_addstr(stdscr, 0, title_x, title)

    # Score and combo
    score_x = BAR_X + BAR_WIDTH + 2
    if power_up_active:
        safe_addstr(stdscr, 1, score_x, f"Score: {score}", curses.color_pair(flash_color))
        safe_addstr(stdscr, 2, score_x, f"Combo: {combo}", curses.color_pair(flash_color))
    else:
        safe_addstr(stdscr, 1, score_x, f"Score: {score}")
        safe_addstr(stdscr, 2, score_x, f"Combo: {combo}")

    # Feedback
    if feedback:
        feedback_x = max_x - len(feedback) - 4
        color = COLOR_HIT if feedback_type == "hit" else (COLOR_MISS if feedback_type == "miss" else 0)
        if color:
            safe_addstr(stdscr, 1, feedback_x, feedback, curses.color_pair(color))
        else:
            safe_addstr(stdscr, 1, feedback_x, feedback)

    safe_addstr(stdscr, 2, max_x - 14, "Q = quit")

    # Calculate lane positions
    available_width = max_x - BAR_OFFSET
    lane_width = available_width // (len(LANE_KEYS) + 1)
    lane_positions = [BAR_OFFSET + lane_width * (i + 1) for i in range(len(LANE_KEYS))]

    # Draw lanes and hit line
    if power_up_active:
        color_attr = curses.color_pair(flash_color)
    else:
        color_attr = 0
    
    for x in lane_positions:
        for y in range(4, max_y - 2):
            safe_addch(stdscr, y, x, "|", color_attr)
        safe_addch(stdscr, hit_row, x, "=", color_attr)

    # Draw lane labels with feedback
    for i, key in enumerate(LANE_KEYS):
        x = lane_positions[i]
        key_y = hit_row + 1
        
        if power_up_active:
            safe_addstr(stdscr, key_y, x - 1, key.upper(), curses.color_pair(flash_color))
        elif last_hit_lane == i and (now - last_hit_time) < KEY_FEEDBACK_DURATION:
            safe_addstr(stdscr, key_y, x - 1, key.upper(), curses.color_pair(COLOR_HIT))
        elif last_miss_lane == i and (now - last_miss_time) < KEY_FEEDBACK_DURATION:
            safe_addstr(stdscr, key_y, x - 1, key.upper(), curses.color_pair(COLOR_MISS))
        else:
            safe_addstr(stdscr, key_y, x - 1, key.upper())

    # Messages at bottom
    msg_y = hit_row + 2
    if bar_full and not power_up_active and not waiting_for_transcend:
        msg = "Press SPACE for POWER-UP!"
        msg_x = max_x // 2 - len(msg) // 2
        safe_addstr(stdscr, msg_y, msg_x, msg, curses.A_BLINK | curses.color_pair(flash_color))
    elif waiting_for_transcend:
        msg1 = "YOU TRANSCENDED!"
        msg2 = "Press Y to TRANSCEND, N to continue"
        msg_x1 = max_x // 2 - len(msg1) // 2
        msg_x2 = max_x // 2 - len(msg2) // 2
        safe_addstr(stdscr, msg_y, msg_x1, msg1, curses.A_BOLD | curses.A_BLINK | curses.color_pair(flash_color))
        safe_addstr(stdscr, msg_y + 1, msg_x2, msg2, curses.color_pair(flash_color))

    # Draw notes
    note_color = curses.color_pair(flash_color) if power_up_active else 0
    for note in notes:
        if 4 <= int(note.y) < max_y - 1:
            lane_x = lane_positions[note.lane_idx]
            note_char = LANE_KEYS[note.lane_idx].upper()
            safe_addch(stdscr, int(note.y), lane_x, note_char, note_color)

    stdscr.refresh()


def handle_transcend_input(stdscr, now, transcending_bar, waiting_for_transcend,
                          transcend_pause_start_time, total_paused_time):
    """Handle input while waiting for transcend decision"""
    ch = stdscr.getch()
    if ch == -1:
        return None, transcending_bar, waiting_for_transcend, total_paused_time
    
    # Update pause time
    pause_delta = (now - transcend_pause_start_time) if transcend_pause_start_time > 0 else 0
    new_total_paused = total_paused_time + pause_delta
    
    key = chr(ch).lower() if 0 <= ch < 256 else ""
    
    if key == "y":
        return "transcend", transcending_bar, False, new_total_paused
    elif key == "n":
        return "decline", 0.0, False, new_total_paused
    elif key == "q":
        return "quit", transcending_bar, waiting_for_transcend, new_total_paused
    
    return None, transcending_bar, waiting_for_transcend, new_total_paused


def calculate_score(hit_dist, combo):
    """Calculate score for a successful hit"""
    base = 80
    timing_bonus = max(0, (HIT_WINDOW + 1 - hit_dist)) * 15
    combo_bonus = combo * 5
    return base + timing_bonus + combo_bonus


def get_feedback_text(hit_dist):
    """Get feedback text based on hit distance"""
    if hit_dist <= 0.5:
        return "PERFECT!"
    elif hit_dist <= 1:
        return "GOOD!"
    else:
        return "OK!"


def play_guitar_hero(stdscr):
    """Main game loop"""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    # Initialize colors
    curses.start_color()
    curses.init_pair(COLOR_HIT, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_MISS, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    if not show_instructions(stdscr):
        return 0

    stdscr.nodelay(True)
    stdscr.timeout(0)

    max_y, max_x = stdscr.getmaxyx()
    hit_row = max_y - 4

    # Game state
    notes = []
    score = 0
    combo = 0
    score_bar = 0.0
    transcending_bar = 0.0
    
    # Timing
    start_time = time.time()
    last_spawn_time = start_time
    last_move_time = start_time
    last_drain_time = start_time
    
    # Feedback
    feedback = ""
    feedback_type = None
    last_feedback_time = 0
    last_hit_lane = None
    last_miss_lane = None
    last_hit_time = 0
    last_miss_time = 0
    
    # Power-up state
    power_up_active = False
    power_up_start_time = 0
    
    # Transcend state
    waiting_for_transcend = False
    transcend_pause_start_time = 0
    total_paused_time = 0.0
    transcend_declined = False

    while True:
        now = time.time()
        
        # Calculate elapsed time with pause accounting
        current_pause = (now - transcend_pause_start_time) if (waiting_for_transcend and transcend_pause_start_time > 0) else 0
        elapsed = (now - start_time) - total_paused_time - current_pause

        if elapsed > GAME_DURATION:
            break

        # Handle transcend pause
        if waiting_for_transcend:
            if transcend_pause_start_time == 0:
                transcend_pause_start_time = now
            
            draw_frame(stdscr, notes, score, combo, max_y, max_x, hit_row,
                      feedback, feedback_type, last_hit_lane, last_miss_lane,
                      now, last_hit_time, last_miss_time, score_bar,
                      power_up_active, transcending_bar, waiting_for_transcend)
            
            result, transcending_bar, waiting_for_transcend, total_paused_time = \
                handle_transcend_input(stdscr, now, transcending_bar, waiting_for_transcend,
                                      transcend_pause_start_time, total_paused_time)
            
            if result == "transcend":
                score += TRANSCEND_BONUS
                # Return special value to indicate transcend happened
                stdscr.nodelay(False)
                stdscr.clear()
                max_y, max_x = stdscr.getmaxyx()
                msg = "YOU TRANSCENDED!"
                safe_addstr(stdscr, max_y // 2 - 1, max_x // 2 - len(msg) // 2, msg, curses.A_BOLD | curses.color_pair(get_flash_color(time.time())))
                safe_addstr(stdscr, max_y // 2, max_x // 2 - 10, f"Final Score: {score}")
                safe_addstr(stdscr, max_y // 2 + 2, max_x // 2 - 16, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
                return "transcend"
            elif result == "decline":
                transcend_declined = True
                transcend_pause_start_time = 0
            elif result == "quit":
                break
            
            time.sleep(0.01)
            continue

        # Update score bar
        drain_delta = now - last_drain_time
        if power_up_active:
            elapsed_bonus = now - power_up_start_time
            remaining = max(0, POWER_UP_DURATION - elapsed_bonus)
            score_bar = (remaining / POWER_UP_DURATION) * 100.0
        else:
            if score_bar < 100.0:
                score_bar = max(0, score_bar - (BAR_DRAIN_RATE * drain_delta))
        last_drain_time = now
        
        # Update transcending bar
        if power_up_active and transcending_bar < 100.0:
            transcending_bar = max(0, transcending_bar - (TRANSCENDING_DRAIN_RATE * drain_delta))

        # Check for transcend opportunity
        if transcending_bar >= 100.0 and power_up_active and not waiting_for_transcend and not transcend_declined:
            waiting_for_transcend = True
        
        # Check power-up expiration
        if power_up_active and (now - power_up_start_time) >= POWER_UP_DURATION:
            power_up_active = False
            score_bar = 0.0
            transcending_bar = 0.0
            transcend_declined = False

        # Clear old feedback
        if feedback and (now - last_feedback_time > FEEDBACK_DURATION):
            feedback = ""
            feedback_type = None

        # Spawn notes
        if now - last_spawn_time >= SPAWN_INTERVAL:
            lane_idx = random.randint(0, len(LANE_KEYS) - 1)
            notes.append(Note(lane_idx, 4))
            last_spawn_time = now

        # Move notes
        if now - last_move_time >= NOTE_SPEED:
            for note in notes:
                if not note.hit and not note.missed:
                    note.y += 1
                    if note.y > hit_row + HIT_WINDOW:
                        note.missed = True
                        note.hit_time = now
                        last_miss_lane = note.lane_idx
                        last_miss_time = now
                        combo = 0
                        feedback = "MISS!"
                        feedback_type = "miss"
                        last_feedback_time = now
                elif note.missed:
                    note.y += 1
            last_move_time = now

        # Clean up notes
        notes = [note for note in notes if
                 (not note.hit and not note.missed) or
                 (note.hit and note.hit_time and (now - note.hit_time) < HIT_DISPLAY_TIME) or
                 (note.missed and int(note.y) < max_y)]

        # Handle input
        ch = stdscr.getch()
        if ch != -1:
            if ch == ord(" ") and score_bar >= 100.0 and not power_up_active and not waiting_for_transcend:
                power_up_active = True
                power_up_start_time = now
                score_bar = 100.0
            
            key = chr(ch).lower() if 0 <= ch < 256 else ""
            if key == "q":
                break
            
            if key in LANE_KEYS:
                lane_idx = LANE_KEYS.index(key)
                best_note = None
                best_dist = HIT_WINDOW + 1
                
                for note in notes:
                    if note.lane_idx == lane_idx and not note.hit and not note.missed:
                        dist = abs(note.y - hit_row)
                        if dist <= HIT_WINDOW and dist < best_dist:
                            best_dist = dist
                            best_note = note

                if best_note:
                    best_note.hit = True
                    best_note.hit_time = now
                    last_hit_lane = best_note.lane_idx
                    last_hit_time = now
                    combo += 1
                    
                    if not power_up_active:
                        score_bar = min(100, score_bar + BAR_HIT_GAIN)
                    if power_up_active:
                        transcending_bar = min(100, transcending_bar + TRANSCENDING_HIT_GAIN)
                    
                    score += calculate_score(best_dist, combo)
                    feedback = get_feedback_text(best_dist)
                    feedback_type = "hit"
                    last_feedback_time = now
                else:
                    last_miss_lane = lane_idx
                    last_miss_time = now
                    combo = 0
                    feedback = "MISS!"
                    feedback_type = "miss"
                    last_feedback_time = now

        # Draw frame
        draw_frame(stdscr, notes, score, combo, max_y, max_x, hit_row,
                  feedback, feedback_type, last_hit_lane, last_miss_lane,
                  now, last_hit_time, last_miss_time, score_bar,
                  power_up_active, transcending_bar, waiting_for_transcend)

        time.sleep(0.01)

    # Game over screen
    stdscr.nodelay(False)
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    msg = "Nice Shread"
    safe_addstr(stdscr, max_y // 2 - 1, max_x // 2 - len(msg) // 2, msg, curses.A_BOLD)
    safe_addstr(stdscr, max_y // 2, max_x // 2 - 10, f"Final Score: {score}")
    safe_addstr(stdscr, max_y // 2 + 2, max_x // 2 - 16, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()

    return score


def main():
    """Main entry point with proper exception handling"""
    try:
        return curses.wrapper(play_guitar_hero)
    except KeyboardInterrupt:
        # User pressed Ctrl+C - restore terminal and exit gracefully
        try:
            curses.endwin()
        except:
            pass
        print("\nGame interrupted by user.")
        return 0
    except Exception as e:
        # Any other error - restore terminal and show error
        try:
            curses.endwin()
        except:
            pass
        print(f"\nError: {e}")
        return 0


if __name__ == "__main__":
    main()
