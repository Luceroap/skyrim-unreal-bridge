print("prefetch left", len(getattr(live, "prefetch_todo", [])), "current batch", len(getattr(live, "_pf_chunk", [])))
