import requests
import urllib

class RequestGuard:
    def __init__(self, link):
        """May ingest any link"""
        parsed = urllib.parse.urlparse(link)
        self.domain = parsed.netloc
        self.scheme = parsed.scheme
        self.forbidden = self.parse_robots()

    def parse_robots(self):
        """Returns a list of forbidden paths"""
        robots_text = requests.get(f"{self.scheme}://{self.domain}/robots.txt").text
        forbidden = [f[10:] for f in robots_text.split("\n") if f.startswith("Disallow: ")]
        return forbidden

    def can_follow_link(self, link):
        """Returns true where the passed link is not forbidden"""
        parsed = urllib.parse.urlparse(link)
        if parsed.netloc != self.domain:
            return False
        if any(parsed.path.startswith(f) for f in self.forbidden):
            return False
        return True

    def make_get_request(self, *args, **kwargs):
        """Wraps requests.get to check against robots.txt first"""
        if self.can_follow_link(args[0]):
            return requests.get(*args, **kwargs)