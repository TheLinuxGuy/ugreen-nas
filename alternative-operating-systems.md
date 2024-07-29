# Alternatives to UGREEN NASync OS (UGOS)

UGOS v1.0 has several shortcomings given its their first version. You may or may not be concerned about the maturity of the NAS operating system if all you want is to store photos on a RAID array with some web interface. However, some users have a bare minimum list of expectations of a NAS. Myself included.

UGOS v1.0 was released without the ability to take snapshots or protect your data against ransomware. This is important for me, it may not be for you. This page shares some resources and options that I may have an opinion on.

Resources:
- https://forum.cloudron.io/topic/10000/a-list-of-cloudron-like-services-competitors/2

## Proxmox / Debian bookworm 12 (my OS of choice)
- http://proxmox.com 

TheLinuxGuy says: 
> `Rock solid, debian based virtual machine hypervisor.`


I've been a proxmox users for over a decade, its built on the most reliable open source linux distribution Debian. The OS itself is not a NAS and it is meant to be a virtual machine hypervisor node. Nothing stops you from extending this and converting your hypervisor into a NAS combo which is what I have chosen to do.


## CasaOS / ZimaOS
- https://github.com/IceWhaleTech/CasaOS
- https://github.com/IceWhaleTech/zimaos-rauc

TheLinuxGuy says: 
> `Promising, still half-baked. Stays true to its Beta™`

July 2024: Tested ZimaOS which basically extends the CasaOS file manager to also do virtual machines and RAID. There are a lot of bugs in this beta v1.2.1.

## Umbrel (untested)
- https://github.com/getumbrel/umbrel

TheLinuxGuy says: 
> `Looks nicer than CasaOS web UI, offers zero storage management of any kind.`

## Xpenology
- https://xpenology.com/forum/

TheLinuxGuy says: 
> `Arguably the best NAS OS in the world. Allows you to run Synology OS and apps on your own hardware, with the risk of losing your data. Make sure you have backups or just buy a Synology.`

## Unraid
- http://unraid.net

TheLinuxGuy says: 
> `The best OS for a media-server (Plex, Jellyfin). Lower power consumption, special parity configuration means your peak performance will be limited to your slowest data disk.`

## Free-unraid
- https://github.com/TheLinuxGuy/free-unraid

TheLinuxGuy says: 
> `Don't want to pay for an unraid license? You can build yourself a similar solution joining multiple open source tools in a linux server.`