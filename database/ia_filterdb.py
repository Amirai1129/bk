
async def get_search_results(chat_id, query, offset=0, filter=False):
    files = col.find({"file_name": {"$regex": query, "$options": "i"}}).skip(offset).limit(10)
    total_results = col.count_documents({"file_name": {"$regex": query, "$options": "i"}})
    
    results = []
    for file in files:
        imdb_info = get_imdb_info(file["file_name"])
        subtitles = get_subtitles(file["file_name"])
        dubbing = get_dubbing(file["file_name"])

        results.append({
            "file_id": file["file_id"],
            "file_name": file["file_name"],
            "file_size": get_size(file["file_size"]),
            "poster": imdb_info.get("poster", None),
            "rating": imdb_info.get("rating", "نامشخص"),
            "genre": imdb_info.get("genre", "نامشخص"),
            "year": imdb_info.get("year", "نامشخص"),
            "actors": imdb_info.get("actors", "نامشخص"),
            "director": imdb_info.get("director", "نامشخص"),
            "summary": imdb_info.get("summary", "خلاصه‌ای موجود نیست"),
            "imdb_link": imdb_info.get("imdb_link", None),
            "seasons": get_seasons(file["file_name"]),
            "episodes": get_episodes(file["file_name"]),
            "qualities": get_qualities(file["file_name"]),
            "languages": get_languages(file["file_name"]),
            "subtitles": subtitles,
            "dubbing": dubbing,
        })
    
    return results, offset, total_results


async def save_file(media):
    file_id = unpack_new_file_id(media.file_id)
    file_name = clean_file_name(media.file_name)

    imdb_info = get_imdb_info(file_name)
    subtitles = get_subtitles(file_name)
    dubbing = get_dubbing(file_name)

    file = {
        'file_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size,
        'caption': media.caption.html if media.caption else "",
        'poster': imdb_info.get("poster", None),
        'rating': imdb_info.get("rating", "نامشخص"),
        'genre': imdb_info.get("genre", "نامشخص"),
        'year': imdb_info.get("year", "نامشخص"),
        'actors': imdb_info.get("actors", "نامشخص"),
        'director': imdb_info.get("director", "نامشخص"),
        'summary': imdb_info.get("summary", "خلاصه‌ای موجود نیست"),
        'imdb_link': imdb_info.get("imdb_link", None),
        'seasons': get_seasons(file_name),
        'episodes': get_episodes(file_name),
        'qualities': get_qualities(file_name),
        'languages': get_languages(file_name),
        'subtitles': subtitles,
        'dubbing': dubbing,
    }

    col.insert_one(file)
