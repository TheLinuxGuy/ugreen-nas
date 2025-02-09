# Flashcache

Synology uses flashcache. Flashcache is an abandoned block caching software.

I've tried to build it following the [dkms instructions](https://github.com/facebookarchive/flashcache/blob/master/README-DKMS) and was unsuccessful. 

```bash
/root/flashcache/src/flashcache_conf.c:1719:27: error: initialization of ‘int (*)(struct dm_target *, struct block_device **)’ from incompatible pointer type ‘int (*)(struct dm_target *, struct block_device **, fmode_t *)’ {aka ‘int (*)(struct dm_target *, struct block_device **, unsigned int *)’} [-Werror=incompatible-pointer-types]
 1719 |         .prepare_ioctl  = flashcache_prepare_ioctl,
      |                           ^~~~~~~~~~~~~~~~~~~~~~~~
/root/flashcache/src/flashcache_conf.c:1719:27: note: (near initialization for ‘flashcache_target.prepare_ioctl’)
/root/flashcache/src/flashcache_conf.c:1720:27: error: initialization of ‘int (*)(struct dm_target *, unsigned int,  char **, char *, unsigned int)’ from incompatible pointer type ‘int (*)(struct dm_target *, unsigned int,  char **)’ [-Werror=incompatible-pointer-types]
 1720 |         .message        = flashcache_message,
      |                           ^~~~~~~~~~~~~~~~~~
/root/flashcache/src/flashcache_conf.c:1720:27: note: (near initialization for ‘flashcache_target.message’)
/root/flashcache/src/flashcache_conf.c:1825:1: warning: no previous prototype for ‘flashcache_init’ [-Wmissing-prototypes]
 1825 | flashcache_init(void)
      | ^~~~~~~~~~~~~~~
/root/flashcache/src/flashcache_conf.c:1907:1: warning: no previous prototype for ‘flashcache_exit’ [-Wmissing-prototypes]
 1907 | flashcache_exit(void)
      | ^~~~~~~~~~~~~~~
cc1: some warnings being treated as errors
make[4]: *** [scripts/Makefile.build:243: /root/flashcache/src/flashcache_conf.o] Error 1
make[3]: *** [/usr/src/linux-headers-6.8.8-2-pve/Makefile:1926: /root/flashcache/src] Error 2
make[2]: *** [Makefile:240: __sub-make] Error 2
make[2]: Leaving directory '/usr/src/linux-headers-6.8.8-2-pve'
make[1]: *** [Makefile:42: modules] Error 2
make[1]: Leaving directory '/root/flashcache/src'
make: *** [Makefile:28: all] Error 2
```