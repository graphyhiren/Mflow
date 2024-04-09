module.exports = async ({ context, github, core }) => {
  const { body, base } = context.payload.pull_request;
  const { owner, repo } = context.repo;

  if (base.ref.match(/^branch-\d+\.\d+$/)) {
    return;
  }

  const marker = "<!-- patch -->";
  if (!body.includes(marker)) {
    return;
  }

  const patchSection = body.split(marker)[1];
  const yesMatch = patchSection.match(/- \[( |x)\] yes/gi);
  const yes = yesMatch ? yesMatch[0].toLowerCase() === "x" : false;
  const noMatch = patchSection.match(/- \[( |x)\] no/gi);
  const no = noMatch ? noMatch[0].toLowerCase() === "x" : false;
  console.log({ yes, no });

  if (yes && no) {
    core.setFailed(
      "Both yes and no are selected. Please select only one in the `Should this PR be included in the next patch release?` section."
    );
  }

  if (!yes && !no) {
    core.setFailed(
      "Please fill in the `Should this PR be included in the next patch release?` section."
    );
  }

  if (no) {
    return;
  }

  const latestRelease = await github.rest.repos.getLatestRelease({
    owner,
    repo,
  });
  const version = latestRelease.data.tag_name.replace("v", "");
  const [major, minor, micro] = version.split(".");
  const label = `patch-${major}.${minor}.${parseInt(micro) + 1}`;
  await github.rest.issues.addLabels({
    owner,
    repo,
    issue_number: context.payload.pull_request.number,
    labels: [label],
  });
};
