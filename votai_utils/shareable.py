class ShareableMixin():
    def get_image(self):
        raise NotImplementedError()

    def get_name(self):
        return self.name
        