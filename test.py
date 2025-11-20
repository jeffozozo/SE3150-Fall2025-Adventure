def parse_map_file(path):
    import re

    rooms = {}
    current_room = None

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Match "Room:X - Name"
            m = re.match(r"Room:(\d+)\s*-\s*(.*)", line)
            if m:
                rid = int(m.group(1))
                name = m.group(2).strip()
                rooms[rid] = {"name": name, "exits": {}}
                current_room = rid
                continue

            # Match directions like "east,4"
            if current_room is not None:
                if "," in line:
                    direction, dest = line.split(",", 1)
                    rooms[current_room]["exits"][direction.strip()] = int(dest)
    return rooms


def generate_ascii_map(rooms):
    """
    Creates an ASCII map with automatic XY placement
    and Z-layers for up/down.
    """

    from collections import deque, defaultdict

    # Define how directions move in x,y,z
    DIR = {
        "north": (0, -1, 0),
        "south": (0,  1, 0),
        "east":  (1,  0, 0),
        "west":  (-1, 0, 0),
        "up":    (0,  0, 1),
        "down":  (0,  0, -1),
    }

    # BFS to assign coordinates
    coords = {}   # room → (x,y,z)
    start = next(iter(rooms))
    coords[start] = (0, 0, 0)

    queue = deque([start])

    while queue:
        r = queue.popleft()
        x, y, z = coords[r]

        for d, dest in rooms[r]['exits'].items():
            dx, dy, dz = DIR[d]
            if dest not in coords:
                coords[dest] = (x + dx, y + dy, z + dz)
                queue.append(dest)

    # Group by z-level
    layers = defaultdict(list)
    for rid, (x,y,z) in coords.items():
        layers[z].append((rid,x,y))

    # Build ASCII for each Z layer
    result = []
    for z in sorted(layers.keys()):
        layer = layers[z]
        xs = [p[1] for p in layer]
        ys = [p[2] for p in layer]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = (max_x-min_x+1)
        height = (max_y-min_y+1)

        # Create grid of text cells
        grid = [["     " for _ in range(width*2)] for _ in range(height*2)]

        # Place rooms
        for rid, x, y in layer:
            gx = (x - min_x) * 2
            gy = (y - min_y) * 2
            grid[gy][gx] = f"[{rid:02}]"

        # Draw connections
        for rid, (x,y,z0) in coords.items():
            if z0 != z:
                continue

            gx = (x - min_x) * 2
            gy = (y - min_y) * 2

            for d, dest in rooms[rid]['exits'].items():
                dx, dy, dz = DIR[d]
                x2, y2, z2 = coords[dest]

                if dz != 0:
                    # up/down connection marker
                    grid[gy][gx] = f"[{rid:02}{'^' if dz>0 else 'v'}]"
                else:
                    # horizontal or vertical
                    gx2 = (x2 - min_x) * 2
                    gy2 = (y2 - min_y) * 2

                    if gx2 == gx:  # vertical
                        mid = (gy + gy2)//2
                        grid[mid][gx] = "  │  "
                    else:          # horizontal
                        mid = (gx + gx2)//2
                        grid[gy][mid] = "───"

        # Convert to text
        result.append(f"=== Z-Layer {z} ===")
        for row in grid:
            result.append("".join(row))

    return "\n".join(result)


# ----------------------------
# Example usage
# ----------------------------

rooms = parse_map_file("map.txt")
ascii_map = generate_ascii_map(rooms)
print(ascii_map)



bee = """\n
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠠⢄⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠉⠢⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢄⠀⠀⠀⠀⠰⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠠⡀⣀⣤⣦⣷⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⣷⣿⣿⠟⣫⠕⠒⢚⠹⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢐⣿⠟⠓⠂⠀⠀⠠⢨⣤⠉⠂⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⡤⢶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠸⡏⡄⢢⣖⠠⠀⠀⠈⠉⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣤⣤⣤⣤⡾⠗⢻⡷⠈⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢏⠀⠈⠋⠀⠀⠄⢀⠀⠉⠀⠀⢱⠀⠀⠐⠖⣖⠒⠋⠉⠁⣀⣀⣤⣾⠿⠋⠁⠀⠀⢸⣧⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢦⡀⠐⠒⠒⠈⠀⠀⢀⣠⢆⡞⠀⠀⠀⣼⣏⠃⠀⠀⠀⣿⣿⣿⣿⡆⠀⡀⠀⠀⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠳⢤⣶⡶⣿⣿⣿⢟⡥⡊⠀⠀⠀⣼⣟⠂⠀⠀⠀⣸⣿⣿⣿⣿⠀⠀⣿⣆⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠧⠀⠙⠻⣿⣈⠀⠀⢀⣾⢟⠎⠀⠀⠀⢠⣿⣿⣿⣿⡟⠀⢀⣿⣿⡆⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠁⠜⠻⣾⣴⣿⣯⡂⠀⢀⠀⢀⣾⣿⣿⣿⡿⠁⠀⣼⣿⣿⢡⣻⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⠈⠀⠘⠈⠛⠷⣷⣿⣷⣶⣌⣾⣿⣿⣿⣿⠃⠀⣼⣿⣿⠃⢸⠃⠻⣿⣧⠀⠀⠀⠀⣀⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡌⡤⠁⠀⠀⠀⠀⠀⠀⠀⠉⢻⣿⣾⣿⣿⣿⡿⠿⠿⣶⣿⣿⣯⣀⣟⣠⣴⣷⣾⣿⡿⠛⠛⠻⣟⣷⠒⠄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⡿⠋⠀⣰⣿⣿⡿⠃⣸⠟⠉⠁⠀⠀⠟⠛⠛⠚⠫⠀⠠⠙⠠⠇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠤⠾⠿⠿⠋⠐⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

print(bee)