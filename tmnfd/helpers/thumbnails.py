from pygbx import Gbx
import cv2


def extract_thumbnail(challenge_file, thumbnail_file):
    try:
        g = Gbx(challenge_file)
        g.root_parser.pos = g.positions['user_data_size'].pos
        user_data_size = g.root_parser.read_uint32()
        num_chunks = g.root_parser.read_uint32()

        entries = dict()
        for _ in range(num_chunks):
            cid = g.root_parser.read_uint32()
            size = g.root_parser.read_uint32()
            entries[cid] = size

        for cid, size in entries.items():
            if cid == 0x03043007:
                if g.root_parser.read_uint32() > 0:
                    thumb_size = g.root_parser.read_uint32()
                    g.root_parser.skip(15)
                    thumb = g.root_parser.read(thumb_size)
                    with open(thumbnail_file, 'wb') as f:
                        f.write(thumb)
                    image = cv2.imread(thumbnail_file)
                    flippedimage = cv2.flip(image, 0)
                    cv2.imwrite(thumbnail_file, flippedimage)
            elif cid == 0x03043005:
                g.root_parser.read_string()
            else:
                g.root_parser.skip(size)
    except Exception:
        pass
