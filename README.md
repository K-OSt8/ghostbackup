# Ghost-Backup

Back up your Ghost blog data.

Uses Block-Storage as archive 

Combines the Elements
- Content-Expoert Json
- Files from Fileystem
- Data from the Database

The back-up is allways full. But it is only taken if changes are detected.
A change is assumed: 
- No back-up found in the Archive.
- Ghost's History has newer entries than the latest Back-up Found in Archive

This logic can be by-passed with the -f commandline switch

## Configuration

Ghost-Backup reads its settings from an INI-style configuration file.

- **Default location:** `~/.ghost-backup.cfg`
- **Custom location:** `Ghost-Backup --config /path/to/file.cfg`

A commented template is available in [`ghost-backup.cfg.example`](ghost-backup.cfg.example).

> **Note:** The file contains an access token, so restrict its permissions, e.g. `chmod 600 ~/.ghost-backup.cfg`.

### Example

```ini
[Ghost]
Host = https://localhost:2368
AccessToken = <your-admin-api-token>
Dir = ~/ghost

[OCI]
BucketName = ghost-backup
NameSpace = <your-tenancy-namespace>

[DB]
Host = mysql-1
Port = 3306
DBName = ghost_prod
DBUserName = readonly-user
SecretOcid = ocid1.vaultsecret.<...>
```

### Section `[Ghost]`

Settings for the Ghost blog instance that is backed up.

| Option | Required | Example | Description |
|--------|----------|---------|-------------|
| `Host` | yes | `https://localhost:2368` | Base URL of the Ghost instance. |
| `AccessToken` | yes | | Ghost Admin API access token used to authenticate against the instance. |
| `Dir` | yes | `~/ghost` | Path to the Ghost installation directory. A leading `~` is expanded to the home directory of the user running the backup. |

### Section `[OCI]`

Target for the backup archives in Oracle Cloud Infrastructure (OCI) Object Storage.

| Option | Required | Example | Description |
|--------|----------|---------|-------------|
| `BucketName` | yes | `ghost-backup` | Name of the Object Storage bucket the archives are uploaded to. |
| `NameSpace` | yes | `mynamespace` | Object Storage namespace of your tenancy. |

### Section `[DB]`

Connection to the MySQL database used by Ghost.

| Option | Required | Example | Description |
|--------|----------|---------|-------------|
| `Host` | yes | `mysql-1` | Hostname or IP address of the MySQL server. |
| `Port` | no | `3306` | TCP port of the MySQL server. |
| `DBName` | yes | `ghost_prod` | Name of the Ghost database. |
| `DBUserName` | yes | `readonly-user` | Database user. A read-only user is sufficient, since the backup only reads data. |
| `SecretOcid` | yes | `ocid1.vaultsecret.<...>` | OCID of the OCI Vault secret that holds the password of `DBUserName`. The password is never stored in the configuration file. |

### Syntax notes

- Section and option names are case-sensitive in the spelling shown above, unless your code normalizes them (Python's `configparser` lowercases option names, but not section names).
- Comments start with `#` or `;` and must be on their own line. Inline comments after a value are not supported and would become part of the value.
- Values do not need quotes.


## Usage

```
Ghost-Backup [-h] [-f] [-c CONFIG] [-v] [-V]
```

### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show the help message and exit. |
| `-f`, `--force` | Run the backup in any case. Skips the check whether the existing archive is up to date. |
| `-c CONFIG`, `--config CONFIG` | Path to the configuration file. Defaults to `~/.ghost-backup.cfg`. |
| `-v`, `--verbose` | Enable verbose output. |
| `-V`, `--version` | Show the program's version number and exit. |

### Examples

Run a regular backup (skipped if the archive is already up to date):

```
Ghost-Backup
```

Force a backup, even if the archive is current:

```
Ghost-Backup --force
```

Use a custom configuration file with verbose output:

```
Ghost-Backup --config /etc/ghost-backup.cfg --verbose
```

Print the installed version:

```
Ghost-Backup --version
```