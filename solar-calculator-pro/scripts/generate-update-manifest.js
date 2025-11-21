#!/usr/bin/env node

/**
 * Generate Update Manifest
 * 
 * This script generates the update manifest files (latest.yml, latest-mac.yml, latest-linux.yml)
 * that electron-updater uses to check for updates.
 * 
 * Usage:
 *   node scripts/generate-update-manifest.js --version 1.0.0 --platform win --output ./release
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const yaml = require('js-yaml');

// Parse command line arguments
const args = process.argv.slice(2);
const options = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace('--', '');
  const value = args[i + 1];
  options[key] = value;
}

const {
  version = '1.0.0',
  platform = 'win',
  output = './release',
  releaseNotes = '',
  releaseNotesUrl = ''
} = options;

/**
 * Calculate SHA512 hash of a file
 * @param {string} filePath - Path to file
 * @returns {Promise<string>} Base64-encoded SHA512 hash
 */
async function calculateSHA512(filePath) {
  return new Promise((resolve, reject) => {
    const hash = crypto.createHash('sha512');
    const stream = fs.createReadStream(filePath);

    stream.on('data', (data) => hash.update(data));
    stream.on('end', () => resolve(hash.digest('base64')));
    stream.on('error', reject);
  });
}

/**
 * Get file size
 * @param {string} filePath - Path to file
 * @returns {number} File size in bytes
 */
function getFileSize(filePath) {
  const stats = fs.statSync(filePath);
  return stats.size;
}

/**
 * Find installer files in output directory
 * @param {string} outputDir - Output directory
 * @param {string} platform - Platform (win, mac, linux)
 * @returns {Array<string>} Array of installer file paths
 */
function findInstallerFiles(outputDir, platform) {
  const files = fs.readdirSync(outputDir);
  const patterns = {
    win: /\.exe$/,
    mac: /\.dmg$/,
    linux: /\.(AppImage|deb)$/
  };

  const pattern = patterns[platform];
  return files
    .filter(file => pattern.test(file))
    .map(file => path.join(outputDir, file));
}

/**
 * Generate manifest for a platform
 * @param {string} platform - Platform (win, mac, linux)
 * @param {string} outputDir - Output directory
 * @param {string} version - Version number
 * @returns {Promise<Object>} Manifest object
 */
async function generateManifest(platform, outputDir, version) {
  const installerFiles = findInstallerFiles(outputDir, platform);

  if (installerFiles.length === 0) {
    throw new Error(`No installer files found for platform: ${platform}`);
  }

  console.log(`Found ${installerFiles.length} installer file(s) for ${platform}:`);
  installerFiles.forEach(file => console.log(`  - ${path.basename(file)}`));

  const files = await Promise.all(
    installerFiles.map(async (filePath) => {
      const fileName = path.basename(filePath);
      const sha512 = await calculateSHA512(filePath);
      const size = getFileSize(filePath);

      console.log(`  SHA512: ${sha512.substring(0, 32)}...`);
      console.log(`  Size: ${(size / 1024 / 1024).toFixed(2)} MB`);

      return {
        url: fileName,
        sha512,
        size
      };
    })
  );

  const manifest = {
    version,
    releaseDate: new Date().toISOString(),
    files,
    path: files[0].url,
    sha512: files[0].sha512
  };

  if (releaseNotes) {
    manifest.releaseNotes = releaseNotes;
  }

  if (releaseNotesUrl) {
    manifest.releaseNotesUrl = releaseNotesUrl;
  }

  return manifest;
}

/**
 * Get manifest filename for platform
 * @param {string} platform - Platform (win, mac, linux)
 * @returns {string} Manifest filename
 */
function getManifestFilename(platform) {
  const filenames = {
    win: 'latest.yml',
    mac: 'latest-mac.yml',
    linux: 'latest-linux.yml'
  };
  return filenames[platform] || 'latest.yml';
}

/**
 * Main function
 */
async function main() {
  try {
    console.log('='.repeat(60));
    console.log('Generating Update Manifest');
    console.log('='.repeat(60));
    console.log(`Version: ${version}`);
    console.log(`Platform: ${platform}`);
    console.log(`Output: ${output}`);
    console.log('='.repeat(60));

    // Ensure output directory exists
    if (!fs.existsSync(output)) {
      throw new Error(`Output directory does not exist: ${output}`);
    }

    // Generate manifest
    const manifest = await generateManifest(platform, output, version);

    // Convert to YAML
    const yamlContent = yaml.dump(manifest, {
      indent: 2,
      lineWidth: -1
    });

    // Write manifest file
    const manifestFilename = getManifestFilename(platform);
    const manifestPath = path.join(output, manifestFilename);
    fs.writeFileSync(manifestPath, yamlContent, 'utf8');

    console.log('='.repeat(60));
    console.log(`✓ Manifest generated successfully: ${manifestFilename}`);
    console.log('='.repeat(60));
    console.log('\nManifest content:');
    console.log(yamlContent);
    console.log('='.repeat(60));

    // Also save as JSON for debugging
    const jsonPath = path.join(output, `${manifestFilename}.json`);
    fs.writeFileSync(jsonPath, JSON.stringify(manifest, null, 2), 'utf8');
    console.log(`✓ JSON version saved: ${path.basename(jsonPath)}`);

  } catch (error) {
    console.error('Error generating manifest:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  generateManifest,
  calculateSHA512,
  getFileSize,
  findInstallerFiles
};
