/**
 * Release Notes Generator
 * 
 * Generates release notes from git commits and changelog
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Get git commits since last tag
 */
function getCommitsSinceLastTag() {
  try {
    // Get last tag
    const lastTag = execSync('git describe --tags --abbrev=0', {
      encoding: 'utf-8',
    }).trim();
    
    // Get commits since last tag
    const commits = execSync(
      `git log ${lastTag}..HEAD --pretty=format:"%h|%s|%an|%ad" --date=short`,
      { encoding: 'utf-8' }
    ).trim();
    
    if (!commits) {
      return [];
    }
    
    return commits.split('\n').map(line => {
      const [hash, subject, author, date] = line.split('|');
      return { hash, subject, author, date };
    });
  } catch (error) {
    // No previous tag, get all commits
    const commits = execSync(
      'git log --pretty=format:"%h|%s|%an|%ad" --date=short',
      { encoding: 'utf-8' }
    ).trim();
    
    if (!commits) {
      return [];
    }
    
    return commits.split('\n').map(line => {
      const [hash, subject, author, date] = line.split('|');
      return { hash, subject, author, date };
    });
  }
}

/**
 * Categorize commits
 */
function categorizeCommits(commits) {
  const categories = {
    features: [],
    fixes: [],
    improvements: [],
    breaking: [],
    other: [],
  };
  
  for (const commit of commits) {
    const subject = commit.subject.toLowerCase();
    
    if (subject.includes('breaking') || subject.includes('!:')) {
      categories.breaking.push(commit);
    } else if (
      subject.startsWith('feat:') ||
      subject.startsWith('feature:') ||
      subject.includes('add ')
    ) {
      categories.features.push(commit);
    } else if (
      subject.startsWith('fix:') ||
      subject.includes('bug') ||
      subject.includes('issue')
    ) {
      categories.fixes.push(commit);
    } else if (
      subject.startsWith('improve:') ||
      subject.startsWith('enhancement:') ||
      subject.includes('improve') ||
      subject.includes('enhance') ||
      subject.includes('optimize')
    ) {
      categories.improvements.push(commit);
    } else {
      categories.other.push(commit);
    }
  }
  
  return categories;
}

/**
 * Generate markdown release notes
 */
function generateMarkdown(version, categories, isBeta = false) {
  const betaTag = isBeta ? ' (Beta)' : '';
  const date = new Date().toISOString().split('T')[0];
  
  let markdown = `# Release Notes - Version ${version}${betaTag}\n\n`;
  markdown += `**Release Date:** ${date}\n\n`;
  
  if (isBeta) {
    markdown += `> **Note:** This is a beta release. Please report any issues through the in-app feedback system.\n\n`;
  }
  
  // Breaking changes
  if (categories.breaking.length > 0) {
    markdown += `## ⚠️ Breaking Changes\n\n`;
    for (const commit of categories.breaking) {
      markdown += `- ${commit.subject} ([${commit.hash}](../../commit/${commit.hash}))\n`;
    }
    markdown += `\n`;
  }
  
  // New features
  if (categories.features.length > 0) {
    markdown += `## ✨ New Features\n\n`;
    for (const commit of categories.features) {
      markdown += `- ${commit.subject} ([${commit.hash}](../../commit/${commit.hash}))\n`;
    }
    markdown += `\n`;
  }
  
  // Bug fixes
  if (categories.fixes.length > 0) {
    markdown += `## 🐛 Bug Fixes\n\n`;
    for (const commit of categories.fixes) {
      markdown += `- ${commit.subject} ([${commit.hash}](../../commit/${commit.hash}))\n`;
    }
    markdown += `\n`;
  }
  
  // Improvements
  if (categories.improvements.length > 0) {
    markdown += `## 🚀 Improvements\n\n`;
    for (const commit of categories.improvements) {
      markdown += `- ${commit.subject} ([${commit.hash}](../../commit/${commit.hash}))\n`;
    }
    markdown += `\n`;
  }
  
  // Other changes
  if (categories.other.length > 0) {
    markdown += `## 📝 Other Changes\n\n`;
    for (const commit of categories.other) {
      markdown += `- ${commit.subject} ([${commit.hash}](../../commit/${commit.hash}))\n`;
    }
    markdown += `\n`;
  }
  
  // Contributors
  const contributors = [...new Set(categories.features.concat(
    categories.fixes,
    categories.improvements,
    categories.breaking,
    categories.other
  ).map(c => c.author))];
  
  if (contributors.length > 0) {
    markdown += `## 👥 Contributors\n\n`;
    markdown += `Thank you to all contributors:\n\n`;
    for (const contributor of contributors) {
      markdown += `- ${contributor}\n`;
    }
    markdown += `\n`;
  }
  
  // Installation instructions
  markdown += `## 📦 Installation\n\n`;
  markdown += `### Windows\n`;
  markdown += `Download and run \`Solar-Calculator-Pro-${version}${isBeta ? '-beta' : ''}-Setup.exe\`\n\n`;
  markdown += `### macOS\n`;
  markdown += `Download and open \`Solar-Calculator-Pro-${version}${isBeta ? '-beta' : ''}.dmg\`\n\n`;
  markdown += `### Linux\n`;
  markdown += `Download \`Solar-Calculator-Pro-${version}${isBeta ? '-beta' : ''}.AppImage\` or \`.deb\` package\n\n`;
  
  // Known issues
  markdown += `## ⚠️ Known Issues\n\n`;
  markdown += `Please check our [issue tracker](https://github.com/yourcompany/solar-calculator-pro/issues) for known issues.\n\n`;
  
  // Support
  markdown += `## 💬 Support\n\n`;
  markdown += `- Documentation: https://docs.yourcompany.com\n`;
  markdown += `- Forum: https://forum.yourcompany.com\n`;
  if (isBeta) {
    markdown += `- Beta Support: beta@yourcompany.com\n`;
  } else {
    markdown += `- Email: support@yourcompany.com\n`;
  }
  markdown += `\n`;
  
  return markdown;
}

/**
 * Main function
 */
function main() {
  const args = process.argv.slice(2);
  
  // Parse arguments
  let version = null;
  let isBeta = false;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--version' && i + 1 < args.length) {
      version = args[i + 1];
      i++;
    } else if (args[i] === '--beta') {
      isBeta = true;
    }
  }
  
  if (!version) {
    // Get version from package.json
    const packageJson = require('../package.json');
    version = packageJson.version;
  }
  
  console.log(`Generating release notes for version ${version}...`);
  
  // Get commits
  const commits = getCommitsSinceLastTag();
  console.log(`Found ${commits.length} commits`);
  
  // Categorize commits
  const categories = categorizeCommits(commits);
  console.log('Categorized commits:', {
    features: categories.features.length,
    fixes: categories.fixes.length,
    improvements: categories.improvements.length,
    breaking: categories.breaking.length,
    other: categories.other.length,
  });
  
  // Generate markdown
  const markdown = generateMarkdown(version, categories, isBeta);
  
  // Write to file
  const outputPath = path.join(__dirname, '../docs/RELEASE_NOTES.md');
  fs.writeFileSync(outputPath, markdown);
  console.log(`✓ Release notes written to ${outputPath}`);
  
  // Also write to version-specific file
  const versionPath = path.join(
    __dirname,
    `../docs/releases/RELEASE_NOTES_${version}.md`
  );
  const versionDir = path.dirname(versionPath);
  if (!fs.existsSync(versionDir)) {
    fs.mkdirSync(versionDir, { recursive: true });
  }
  fs.writeFileSync(versionPath, markdown);
  console.log(`✓ Version-specific release notes written to ${versionPath}`);
  
  // Update changelog
  updateChangelog(version, markdown);
  
  console.log('✓ Release notes generation complete');
}

/**
 * Update changelog
 */
function updateChangelog(version, releaseNotes) {
  const changelogPath = path.join(__dirname, '../CHANGELOG.md');
  
  let changelog = '';
  if (fs.existsSync(changelogPath)) {
    changelog = fs.readFileSync(changelogPath, 'utf-8');
  } else {
    changelog = '# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n';
  }
  
  // Insert new release notes at the top (after header)
  const lines = changelog.split('\n');
  const headerEndIndex = lines.findIndex((line, i) => i > 0 && line.trim() === '');
  
  if (headerEndIndex !== -1) {
    lines.splice(headerEndIndex + 1, 0, releaseNotes);
    changelog = lines.join('\n');
  } else {
    changelog += '\n' + releaseNotes;
  }
  
  fs.writeFileSync(changelogPath, changelog);
  console.log(`✓ Changelog updated`);
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  getCommitsSinceLastTag,
  categorizeCommits,
  generateMarkdown,
};
