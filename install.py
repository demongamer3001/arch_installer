print("Loading...")

import requests
from os import system
from time import sleep

def error(error,exit=False):
    print(f"E: {error}")
    if exit: exit(1)
def warning(warning):
    print(f"W: {warning}")

if requests.get("https://google.com").status_code == 404:
    exit(1)
system("pacman -Syy")

_kernels = "linux linux-lts linux-hardened linux-zen".split(" ")
_editors = "nano vim vi nvim".split(" ")
_packages = "net-tools python3 neofetch git".split(" ")
_des = "xfce4".split(" ") # Desktop environments

def list_to_str(x):
    res=""
    for a in x: res+=x+" "
    return res.strip()
def choose(arr: list, STRING=True):
    print()
    c = 0
    for item in arr:
        print(f"[{c}] {item}")
    x = input(": ").split(" ")
    selected = []
    for selection in x:
        try:
            selection = int(selection)
        except:
            selected.append(str(selection))
        selected.append(arr[selection])
    if len(selected) == 0: return None
    if STRING: return list_to_str(selected)
    return selected
def install(packages):
    system(f"pacman -S {packages}")


while True:
    keymap = input("Keymap (l for list): ")
    if keymap == "l":
        system("ls /usr/share/kbd/keymaps/**/*.map.gz | less")
    else:
        break
system(f"loadkeys {keymap}")
hostname = input("Hostname: ")
username = input("Username for normal user: ")
kernels = choose(_kernels)
editors = choose(_editors)
packages = choose(_packages)
time_zone = input("Time Zone (Example: Europe/Berlin): ")
des = choose(_des)

print("Installing... this may take some time.")
sleep(3)

system("timedatectl set-ntp true")
system("fdisk -l")
disk = input("Disk (Example: /dev/sda): ")
swap = "+" + input("Swap amount (Example: 2G): ")
if swap == "+": swap = None

with open("FDISK_SCRIPT","w") as f:
    f.write(f"g\nn\n1\n\n+550M\nn\nn\n\n\n{swap}\nn\n\n\nt\n1\n1\nt\n2\n19\nw")

system(f"fdisk {disk} >> cat FDISK_SCRIPT")

system(f"mkfs.fat -F32 {disk}1")

system(f"mkswap {disk}2 ; swapon {disk}2")

system("mount {disk}3 /mnt")

system(f"pacstrap /mnt base {kernels} linux-firmware")

system("genfstab -U /mnt >> /mnt/etc/fstab")

system(f"""
chroot /mnt /bin/bash <<END

ln -sf /usr/share/zoneinfo/{time_zone} /etc/localtime
hwclock --systohc

sed '/en_US.UTF/s/^#//' -i /etc/locale.gen
locale-gen

echo {hostname} > /etc/hostname
echo >> /etc/hosts
echo 127.0.0.1 localhost >> /etc/hosts
echo ::1 localhost >> /etc/hosts
echo 127.0.1.1 {hostname}.localdomain {hostname} >> /etc/hosts

clear
passwd
useradd -m {username}
clear
passwd {username}
usermod -aG wheel,audio,video,optical,storage {username}

pacman -S sudo

sed '/%wheel ALL=(ALL) ALL/s/^#//' -i /etc/sudoers

pacman -S grub efibootmgr dosfstools os-prober mtools
mkdir /boot/EFI
mount {disk}1 /boot/EFI
grub-install --target=x86_64-efi --bootloader-id=grub_uefi --recheck --removable
grub-mkconfig -o /boot/grub/grub.cfg

pacman -S networkmanager
systemctl enable NetworkManager

END
""")
system("unmount -l /mnt")
system("reboot now")