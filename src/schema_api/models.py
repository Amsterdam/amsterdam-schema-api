from django.db import models

git_url = "https://github.com/Amsterdam/amsterdam-schema/commit/"


class ChangelogItem(models.Model):
    dataset_id = models.CharField()
    status = models.CharField()
    object_id = models.CharField()
    label = models.CharField()
    commit_hash = models.CharField()
    committed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "dataset_id",
            "status",
            "object_id",
            "label",
            "commit_hash",
            "committed_at",
        ]

    def __str__(self):
        return f"{self.description()} ({self.committed_at})"

    def description(self):
        # Table updates
        if len(self.object_id.split("/")) == 3:
            return f"{self.label.capitalize()} table {self.object_id}."

        # Dataset updates
        else:
            if self.label == "status":
                return f"Set status of dataset version {self.object_id} to {self.status}."
            else:
                return f"Create {self.status} dataset version {self.object_id}."
