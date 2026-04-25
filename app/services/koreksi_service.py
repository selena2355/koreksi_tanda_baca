class KoreksiService:
    def koreksi(self, teks, kesalahan_list=None):
        if teks is None:
            return ""
        if not kesalahan_list:
            return teks

        hasil = teks
        for item in sorted(
            kesalahan_list,
            key=lambda kesalahan: (
                getattr(kesalahan, "start", 0),
                getattr(kesalahan, "end", 0),
            ),
            reverse=True,
        ):
            start = getattr(item, "start", None)
            end = getattr(item, "end", None)
            if start is None or end is None:
                continue
            if start < 0 or end < start or end > len(hasil):
                continue

            pengganti = getattr(item, "pengganti", "")
            if pengganti is None:
                pengganti = ""
            hasil = f"{hasil[:start]}{pengganti}{hasil[end:]}"

        return hasil
