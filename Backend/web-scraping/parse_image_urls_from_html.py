import re

def parse_image_urls_from_html(html):
    urls = re.findall(r"https://ssl\.cdn-redfin\.com/photo/[^\s\"'>]+?\.jpg", html)

    seen = set()
    unique = []
    
    for u in urls:
        u = u.rstrip("),")
        if u not in seen:
            seen.add(u)
            unique.append(u)

    big = []

    for u in unique:
        if "/bigphoto/" in u:
            big.append(u)

    if len(big) > 0:
        rest = []

        for u in unique:
            if u not in big:
                rest.append(u)

        return big + rest

    return unique