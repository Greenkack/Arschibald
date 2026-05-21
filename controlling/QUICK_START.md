# Employee Controlling System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get the Employee Controlling System up and running quickly.

## Step 1: Initialize Database (1 minute)

```bash
python controlling/database.py
```

**Expected output:**
```
Controlling database initialized successfully!
Created 14 standard criteria.
```

## Step 2: Access the System (30 seconds)

1. Start the Streamlit app
2. Click on **"Controlling"** in the main menu
3. You should see the controlling interface with 3 tabs

## Step 3: Configure as Admin (2 minutes)

### Create a Position

1. Go to **"Administration & Verwaltung"**
2. Enter admin password
3. Click **"Controlling Einstellungen"**
4. Go to **"💼 Positionen"** tab
5. Click **"Neue Position anlegen"**
6. Enter:
   - Name: "Vertriebsmitarbeiter"
   - Description: "Verkauf und Kundenbetreuung"
7. Click **"Position erstellen"**

### Assign Criteria to Position

1. Go to **"🔗 Zuordnungen"** tab
2. Select "Vertriebsmitarbeiter" from dropdown
3. Click **"Alle Kriterien zuordnen"**
4. All 14 standard criteria are now assigned

### Create an Employee

1. Go to **"👥 Mitarbeiter"** tab
2. Click **"Neuen Mitarbeiter anlegen"**
3. Enter:
   - Vorname: "Max"
   - Nachname: "Mustermann"
   - Wohnort: "Berlin"
   - Geburtsdatum: Select a date (e.g., 1990-01-01)
   - Position: "Vertriebsmitarbeiter"
   - Eintrittsdatum: Select today's date
4. Click **"Mitarbeiter erstellen"**

## Step 4: Enter Performance Data (1 minute)

1. Go to **"Controlling"** in main menu
2. Go to **"📝 Leistungsdaten erfassen"** tab
3. Select "Max Mustermann" from dropdown
4. Enter sample data:
   - Getätigte Anrufe gesamt: 50
   - Kunden terminiert: 10
   - Angefahrene Termine gesamt: 8
   - Verkauf: 2
   - QC bestanden: 2
5. Click **"Leistungsdaten speichern"**

## Step 5: Generate Your First Report (30 seconds)

1. Go to **"📈 Berichte erstellen"** tab
2. Select "Einzelmitarbeiter-Bericht"
3. Select "Max Mustermann"
4. Select "Täglich" as time period
5. Click **"Bericht generieren"**

**You should see:**
- Quota calculations (e.g., Abschlussquote: 25.0%)
- Descriptive ratios (e.g., "Jeder 4. angefahrene Termin ist ein Verkauf")
- Three beautiful charts (bar, column, donut)
- Notifications (if thresholds are met)

## 🎉 Congratulations!

You've successfully:
- ✅ Initialized the database
- ✅ Created a position with criteria
- ✅ Added an employee
- ✅ Recorded performance data
- ✅ Generated your first report

## 📚 Next Steps

### For Users
- Read the [User Guide](USER_GUIDE.md) for detailed instructions
- Explore different time periods (weekly, monthly, etc.)
- Try exporting reports (JSON, Excel, PDF)
- Check the archive for saved reports

### For Administrators
- Read the [Admin Guide](ADMIN_GUIDE.md) for configuration details
- Configure notification thresholds (🔔 Benachrichtigungen tab)
- Create more positions and employees
- Customize criteria assignments

### For Developers
- Review the [README](README.md) for technical details
- Check the [Project Summary](PROJECT_SUMMARY.md) for architecture
- Run the test suite to verify everything works
- Explore the code with inline documentation

## 💡 Tips

### Daily Workflow
1. Enter performance data at end of day
2. Generate daily report to check progress
3. Review notifications for insights

### Weekly Workflow
1. Generate weekly report every Monday
2. Compare with previous weeks
3. Identify trends and patterns

### Monthly Workflow
1. Generate monthly report at month end
2. Create comparison report for team
3. Export reports for presentations

## ❓ Common Questions

**Q: Can I add more employees?**
A: Yes! Go to Admin → Controlling Einstellungen → Mitarbeiter

**Q: Can I create custom criteria?**
A: Yes! Go to Admin → Controlling Einstellungen → Auswertungskriterien

**Q: How do I change notification thresholds?**
A: Go to Admin → Controlling Einstellungen → Benachrichtigungen

**Q: Can I delete old reports?**
A: Yes! Go to Controlling → Archiv and click the delete icon

**Q: What if I make a mistake in data entry?**
A: Just enter the correct data for the same date - it will overwrite the old values

## 🆘 Need Help?

- **User questions:** See [USER_GUIDE.md](USER_GUIDE.md)
- **Admin questions:** See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- **Technical issues:** Contact your system administrator
- **Feature requests:** Contact the development team

## 📊 Sample Data for Testing

Want to test with more realistic data? Here's a week of sample data:

**Monday:**
- Getätigte Anrufe gesamt: 45
- Kunden terminiert: 9
- Angefahrene Termine gesamt: 7
- Verkauf: 2
- QC bestanden: 2

**Tuesday:**
- Getätigte Anrufe gesamt: 52
- Kunden terminiert: 11
- Angefahrene Termine gesamt: 9
- Verkauf: 3
- QC bestanden: 3

**Wednesday:**
- Getätigte Anrufe gesamt: 48
- Kunden terminiert: 10
- Angefahrene Termine gesamt: 8
- Verkauf: 2
- QC bestanden: 2

**Thursday:**
- Getätigte Anrufe gesamt: 55
- Kunden terminiert: 12
- Angefahrene Termine gesamt: 10
- Verkauf: 4
- QC bestanden: 3

**Friday:**
- Getätigte Anrufe gesamt: 50
- Kunden terminiert: 10
- Angefahrene Termine gesamt: 8
- Verkauf: 3
- QC bestanden: 3

After entering this data, generate a **weekly report** to see trends!

## 🎯 Success Checklist

After completing this quick start, you should be able to:

- [x] Access the Controlling module
- [x] Navigate the admin panel
- [x] Create positions and employees
- [x] Assign criteria to positions
- [x] Enter performance data
- [x] Generate reports
- [x] View visualizations
- [x] Understand notifications
- [x] Export reports
- [x] Access the archive

If you can do all of the above, you're ready to use the system productively!

---

**Time to complete:** ~5 minutes
**Difficulty:** Easy
**Prerequisites:** Admin access to the application

**Ready to dive deeper?** Check out the [User Guide](USER_GUIDE.md) or [Admin Guide](ADMIN_GUIDE.md)!
