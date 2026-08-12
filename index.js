const { 
  Client, 
  GatewayIntentBits, 
  Partials, 
  EmbedBuilder, 
  ActionRowBuilder, 
  ButtonBuilder, 
  ButtonStyle, 
  ModalBuilder, 
  TextInputBuilder, 
  TextInputStyle, 
  PermissionFlagsBits 
} = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.MessageContent
  ],
  partials: [Partials.Channel, Partials.Message, Partials.GuildMember]
});

// ====================== الإعدادات ======================
const REVIEW_CHANNEL_ID = "حط_ايدي_روم_المراجعة_هنا";
const ADMIN_ROLE_ID = "حط_ايدي_رول_الإدارة_هنا";      // اختياري
const SCRIPT_ROLE_ID = "حط_ايدي_رول_خبير_السكربتات_هنا"; // اختياري
const STAFF_ROLE_ID = "حط_ايدي_رول_الاستاف_هنا";       // اختياري
// ======================================================

client.once('ready', () => {
  console.log(`✅ البوت شغال: ${client.user.tag}`);
});

// أمر إرسال لوحة التقديمات
client.on('messageCreate', async (message) => {
  if (message.content === '!لوحة-التقديمات' && message.member.permissions.has(PermissionFlagsBits.Administrator)) {
    const embed = new EmbedBuilder()
      .setTitle('📋 نظام التقديمات | Z9X')
      .setDescription('اختر نوع التقديم من الأزرار تحت:')
      .setColor('#2b2d31')
      .setFooter({ text: 'Z9X Applications System' });

    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder()
        .setCustomId('apply_admin')
        .setLabel('تقديم إدارة')
        .setStyle(ButtonStyle.Primary)
        .setEmoji('🛡️'),
      new ButtonBuilder()
        .setCustomId('apply_script')
        .setLabel('تقديم خبير سكربتات')
        .setStyle(ButtonStyle.Success)
        .setEmoji('📜')
    );

    await message.channel.send({ embeds: [embed], components: [row] });
    if (message.deletable) message.delete().catch(() => {});
  }
});

client.on('interactionCreate', async (interaction) => {
  // فتح الفورم
  if (interaction.isButton()) {
    if (interaction.customId === 'apply_admin' || interaction.customId === 'apply_script') {
      const type = interaction.customId === 'apply_admin' ? 'إدارة' : 'خبير سكربتات';

      const modal = new ModalBuilder()
        .setCustomId(`modal_${interaction.customId}`)
        .setTitle(`تقديم ${type}`);

      const nameInput = new TextInputBuilder()
        .setCustomId('name')
        .setLabel('اسمك')
        .setStyle(TextInputStyle.Short)
        .setRequired(true)
        .setMaxLength(50);

      const ageInput = new TextInputBuilder()
        .setCustomId('age')
        .setLabel('عمرك')
        .setStyle(TextInputStyle.Short)
        .setRequired(true)
        .setMaxLength(3);

      const expInput = new TextInputBuilder()
        .setCustomId('experience')
        .setLabel('خبرتك')
        .setStyle(TextInputStyle.Paragraph)
        .setRequired(true)
        .setMaxLength(1000);

      const whyInput = new TextInputBuilder()
        .setCustomId('why')
        .setLabel('ليش تبي تنضم؟')
        .setStyle(TextInputStyle.Paragraph)
        .setRequired(true)
        .setMaxLength(1000);

      const extraInput = new TextInputBuilder()
        .setCustomId('extra')
        .setLabel('معلومات إضافية (اختياري)')
        .setStyle(TextInputStyle.Paragraph)
        .setRequired(false)
        .setMaxLength(500);

      modal.addComponents(
        new ActionRowBuilder().addComponents(nameInput),
        new ActionRowBuilder().addComponents(ageInput),
        new ActionRowBuilder().addComponents(expInput),
        new ActionRowBuilder().addComponents(whyInput),
        new ActionRowBuilder().addComponents(extraInput)
      );

      await interaction.showModal(modal);
    }

    // أزرار القبول والرفض
    if (interaction.customId.startsWith('accept_') || interaction.customId.startsWith('reject_')) {
      if (STAFF_ROLE_ID && !interaction.member.roles.cache.has(STAFF_ROLE_ID) && !interaction.member.permissions.has(PermissionFlagsBits.Administrator)) {
        return interaction.reply({ content: '❌ ما عندك صلاحية.', ephemeral: true });
      }

      const [action, userId, type] = interaction.customId.split('_');
      const member = await interaction.guild.members.fetch(userId).catch(() => null);

      if (action === 'accept') {
        if (type === 'admin' && ADMIN_ROLE_ID && member) {
          await member.roles.add(ADMIN_ROLE_ID).catch(() => {});
        }
        if (type === 'script' && SCRIPT_ROLE_ID && member) {
          await member.roles.add(SCRIPT_ROLE_ID).catch(() => {});
        }

        const embed = EmbedBuilder.from(interaction.message.embeds[0])
          .setColor('#57F287')
          .setTitle(`✅ تم قبول التقديم | ${type === 'admin' ? 'إدارة' : 'خبير سكربتات'}`)
          .addFields({ name: 'تم القبول بواسطة', value: `${interaction.user}` });

        await interaction.update({ embeds: [embed], components: [] });
        
        if (member) {
          member.send(`🎉 تم قبول تقديمك كـ **${type === 'admin' ? 'إدارة' : 'خبير سكربتات'}** في سيرفر **Z9X**`).catch(() => {});
        }
      } else {
        const embed = EmbedBuilder.from(interaction.message.embeds[0])
          .setColor('#ED4245')
          .setTitle(`❌ تم رفض التقديم | ${type === 'admin' ? 'إدارة' : 'خبير سكربتات'}`)
          .addFields({ name: 'تم الرفض بواسطة', value: `${interaction.user}` });

        await interaction.update({ embeds: [embed], components: [] });

        if (member) {
          member.send(`للأسف تم رفض تقديمك في سيرفر **Z9X**.`).catch(() => {});
        }
      }
    }
  }

  // استقبال الفورم
  if (interaction.isModalSubmit()) {
    if (interaction.customId === 'modal_apply_admin' || interaction.customId === 'modal_apply_script') {
      const type = interaction.customId === 'modal_apply_admin' ? 'admin' : 'script';
      const typeName = type === 'admin' ? 'إدارة' : 'خبير سكربتات';

      const name = interaction.fields.getTextInputValue('name');
      const age = interaction.fields.getTextInputValue('age');
      const experience = interaction.fields.getTextInputValue('experience');
      const why = interaction.fields.getTextInputValue('why');
      const extra = interaction.fields.getTextInputValue('extra') || 'لا يوجد';

      const embed = new EmbedBuilder()
        .setTitle(`📥 تقديم جديد | ${typeName}`)
        .setColor(type === 'admin' ? '#5865F2' : '#57F287')
        .addFields(
          { name: 'مقدم الطلب', value: `${interaction.user} (\`${interaction.user.id}\`)`, inline: false },
          { name: 'الاسم', value: name, inline: true },
          { name: 'العمر', value: age, inline: true },
          { name: 'الخبرة', value: experience, inline: false },
          { name: 'ليش تبي تنضم؟', value: why, inline: false },
          { name: 'معلومات إضافية', value: extra, inline: false }
        )
        .setTimestamp()
        .setFooter({ text: `User ID: ${interaction.user.id}` });

      const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder()
          .setCustomId(`accept_${interaction.user.id}_${type}`)
          .setLabel('قبول')
          .setStyle(ButtonStyle.Success),
        new ButtonBuilder()
          .setCustomId(`reject_${interaction.user.id}_${type}`)
          .setLabel('رفض')
          .setStyle(ButtonStyle.Danger)
      );

      const reviewChannel = interaction.guild.channels.cache.get(REVIEW_CHANNEL_ID);
      if (reviewChannel) {
        await reviewChannel.send({ embeds: [embed], components: [row] });
        await interaction.reply({ content: '✅ تم إرسال تقديمك بنجاح! انتظر الرد.', ephemeral: true });
      } else {
        await interaction.reply({ content: '❌ روم المراجعة غير موجود.', ephemeral: true });
      }
    }
  }
});

client.login("MTUzNjU5NjMwNzc1MjUyMTczOA.GCyiaX.DNh_1UInAcPvz_nI8LN6waUFB3m8kJedm9t7fM");
