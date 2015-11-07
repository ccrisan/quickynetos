################################################################################
#
# parprouted
#
################################################################################

PARPROUTED_VERSION = 0.7
PARPROUTED_SOURCE = parprouted-v$(PARPROUTED_VERSION).tar.gz
PARPROUTED_SITE = http://www.hazard.maks.net/parprouted/$(PARPROUTED_SOURCE)

define PARPROUTED_BUILD_CMDS
	$(MAKE) -C $(@D) \
		CC="$(TARGET_CC)" COPT_FLAGS="$(TARGET_CFLAGS)"
endef

define PARPROUTED_INSTALL_TARGET_CMDS
	$(INSTALL) -m 755 -D $(@D)/parprouted $(TARGET_DIR)/usr/sbin/parprouted
endef

$(eval $(generic-package))

