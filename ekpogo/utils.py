
def nullbool(value, default=False):
	if type(value) == type(None):
		return default
	elif type(value) == str:
		return bool(int(value))
	else:
		return bool(value)

def cleanleaderboardqueryset(queryset, **kwargs):
	value = list(queryset)
	for x in value:
		if x.update__xp__max is None or x.update__xp__max is 0:
			value.remove(x)
	return sorted(value, **kwargs)
