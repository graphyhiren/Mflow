import { MLFLOW_INTERNAL_PREFIX } from "./TagUtils";

export const NOTE_CONTENT_TAG = MLFLOW_INTERNAL_PREFIX + 'note.content';

export class NoteInfo {
  constructor(content) {
    this.content = content;
  }

  static fromRunTags = (tags) => {
    const contentTag = Object.values(tags).find((t) => t.getKey() === NOTE_CONTENT_TAG);
    if (contentTag === undefined) {
      return undefined;
    }
    return new NoteInfo(contentTag.getValue());
  };

  static fromExperimentTags = (tags) => {
    const contentTag = tags.find((t) => t.getKey() === NOTE_CONTENT_TAG);
    if (contentTag === undefined) {
      return undefined;
    }
    return new NoteInfo(contentTag.getValue());
  };
}
