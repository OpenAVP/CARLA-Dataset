import carla
import random
import time


class ParkingArea:

    def __init__(self,
                 name: str,
                 x: float,
                 y: float,
                 yaw: float,
                 *,
                 no_random_pose: bool = False):
        self.name = name
        self.x = x
        self.y = y
        self.yaw = yaw
        self.no_random_pose = no_random_pose

    def get_spawn_point(self,
                        z: float = -2.0,
                        *,
                        rand_pos_x: float = 0,
                        rand_pos_y: float = 0,
                        rand_yaw: float = 0):

        if self.no_random_pose:
            rand_pos_x = 0
            rand_pos_y = 0

        x = self.x + random.uniform(-rand_pos_x, rand_pos_x)
        y = self.y + random.uniform(-rand_pos_y, rand_pos_y)
        yaw = self.yaw + random.uniform(-rand_yaw, rand_yaw)

        loc = carla.Location(x=x, y=y, z=z)
        rot = carla.Rotation(yaw=yaw)

        tf = carla.Transform(location=loc, rotation=rot)
        return tf


AVAILABLE_PARKING_AREAS = [
    ParkingArea('001', -30.85, -74.40, 90),
    ParkingArea('002', -27.41, -74.40, 90),
    ParkingArea('003', -25.03, -74.40, 90),
    ParkingArea('004', -21.57, -74.40, 90),
    ParkingArea('005', -19.19, -74.40, 90),
    ParkingArea('006', -03.90, -73.60, 90), #! BUG
    ParkingArea('007', -00.62, -73.50, 90),
    ParkingArea('008', +01.67, -73.50, 90),
    ParkingArea('009', +07.21, -73.50, 90),
    ParkingArea('010', +11.79, -73.50, 90),
    ParkingArea('011', +14.12, -73.50, 90),
    ParkingArea('012', +17.67, -73.50, 90),
    ParkingArea('013', +20.00, -73.50, 90),
    ParkingArea('014', +23.68, -73.50, 90),
    ParkingArea('015', +26.02, -73.50, 90),
    ParkingArea('016', +29.65, -73.50, 90),
    ParkingArea('017', +32.00, -73.50, 90),
    ParkingArea('018', +35.66, -73.50, 90),
    ParkingArea('019', +38.00, -73.50, 90),
    ParkingArea('020', +37.71, -62.18, 270),
    ParkingArea('021', +35.34, -62.18, 270),
    ParkingArea('022', +32.15, -62.18, 270),
    ParkingArea('023', +29.81, -62.18, 270),
    ParkingArea('024', +25.81, -62.18, 270),
    ParkingArea('025', +14.09, -62.18, 270),
    ParkingArea('026', +11.70, -62.18, 270),
    ParkingArea('027', +08.48, -62.18, 270),
    ParkingArea('028', +06.04, -62.18, 270),
    ParkingArea('029', +01.70, -62.18, 270),
    ParkingArea('030', -00.67, -62.18, 270),
    ParkingArea('031', -03.88, -62.18, 270),
    ParkingArea('032', -06.21, -62.18, 270),
    ParkingArea('033', -19.20, -61.94, 270),
    ParkingArea('034', -21.58, -61.94, 270),
    ParkingArea('035', -21.86, -55.54, 90),
    ParkingArea('036', -19.49, -55.54, 90),
    ParkingArea('037', -17.10, -55.54, 90),
    ParkingArea('038', -13.76, -55.54, 90),
    ParkingArea('039', -11.39, -55.54, 90),
    ParkingArea('040', -09.00, -55.54, 90),
    ParkingArea('041', -05.66, -55.54, 90),
    ParkingArea('042', -03.27, -55.54, 90),
    ParkingArea('043', -00.91, -55.54, 90),
    ParkingArea('044', +02.46, -55.54, 90),
    ParkingArea('045', +04.82, -55.54, 90),
    ParkingArea('046', +07.20, -55.54, 90),
    ParkingArea('047', +10.54, -55.54, 90),
    ParkingArea('048', +12.91, -55.54, 90),
    ParkingArea('049', +15.27, -55.54, 90),
    ParkingArea('050', +26.75, -55.54, 90),
    ParkingArea('051', +29.09, -55.54, 90),
    ParkingArea('052', +31.48, -55.54, 90),
    ParkingArea('053', +34.86, -55.54, 90),
    ParkingArea('054', +37.17, -55.54, 90),
    ParkingArea('055', +39.58, -55.54, 90),
    ParkingArea('056', +42.95, -55.54, 90),
    ParkingArea('057', +45.33, -55.54, 90),
    ParkingArea('058', +47.67, -55.54, 90),
    ParkingArea('059', +51.06, -55.54, 90),
    ParkingArea('060', +53.41, -55.54, 90),
    ParkingArea('061', +55.79, -55.54, 90),
    ParkingArea('062', +26.66, -44.50, 270),
    ParkingArea('063', +15.16, -44.50, 270),
    ParkingArea('064', +12.77, -44.50, 270),
    ParkingArea('065', +10.42, -44.50, 270),
    ParkingArea('066', +07.21, -44.50, 270),
    ParkingArea('067', +02.45, -44.50, 270),
    ParkingArea('068', +02.45, -44.50, 270),
    ParkingArea('069', -00.90, -44.50, 270),
    ParkingArea('070', -03.27, -44.50, 270),
    ParkingArea('071', -05.67, -44.50, 270),
    ParkingArea('071', -05.67, -44.50, 270),
    ParkingArea('072', -09.00, -44.50, 270),
    ParkingArea('073', -11.37, -44.50, 270),
    ParkingArea('074', -13.79, -44.50, 270),
    ParkingArea('075', -17.15, -44.50, 270),
    ParkingArea('076', -19.48, -44.50, 270),
    ParkingArea('077', -21.86, -44.50, 270),
    ParkingArea('078', -21.86, -38.60, 90),
    ParkingArea('079', -19.48, -38.60, 90),
    ParkingArea('080', -17.15, -38.60, 90),
    ParkingArea('081', -13.79, -38.60, 90),
    ParkingArea('082', -11.37, -38.60, 90),
    ParkingArea('083', -09.06, -38.60, 90),
    ParkingArea('084', -05.67, -38.60, 90),
    ParkingArea('085', -03.27, -38.60, 90),
    ParkingArea('086', -00.98, -38.60, 90),
    ParkingArea('087', +02.45, -38.60, 90),
    ParkingArea('088', +04.82, -38.60, 90),
    ParkingArea('089', +07.15, -38.60, 90),
    ParkingArea('090', +10.42, -38.60, 90),
    ParkingArea('091', +12.91, -38.60, 90),
    ParkingArea('092', +15.20, -38.60, 90),
    ParkingArea('093', +55.79, -27.74, 270),
    ParkingArea('094', +53.41, -27.74, 270),
    ParkingArea('095', +51.06, -27.74, 270),
    ParkingArea('096', +47.67, -27.74, 270),
    ParkingArea('097', +45.33, -27.74, 270),
    ParkingArea('098', +42.95, -27.74, 270),
    ParkingArea('099', +37.17, -27.74, 270),
    ParkingArea('100', +34.86, -27.74, 270),
    ParkingArea('101', +31.40, -27.74, 270),
    ParkingArea('102', +29.09, -27.74, 270),
    ParkingArea('103', +26.66, -27.74, 270),
    ParkingArea('104', +15.16, -27.74, 270),
    ParkingArea('105', +12.90, -27.74, 270),
    ParkingArea('106', +10.57, -27.74, 270),
    ParkingArea('107', +07.17, -27.74, 270),
    ParkingArea('108', +04.82, -27.74, 270),
    ParkingArea('109', +02.45, -27.74, 270),
    ParkingArea('110', -00.89, -27.74, 270),
    ParkingArea('111', -03.27, -27.74, 270),
    ParkingArea('112', -05.61, -27.74, 270),
    ParkingArea('113', -09.00, -27.74, 270),
    ParkingArea('114', -11.37, -27.74, 270),
    ParkingArea('115', -13.76, -27.74, 270),
    ParkingArea('116', -17.10, -27.74, 270),
    ParkingArea('117', -19.49, -27.74, 270),
    ParkingArea('118', -21.86, -27.74, 270),
    ParkingArea('119', -24.32, -24.60, 90),
    ParkingArea('120', -21.86, -22.40, 90),
    ParkingArea('121', -19.49, -22.40, 90),
    ParkingArea('122', -17.10, -22.40, 90),
    ParkingArea('123', -13.76, -22.40, 90),
    ParkingArea('124', -11.37, -22.40, 90),
    ParkingArea('125', -09.00, -22.40, 90),
    ParkingArea('126', -05.66, -22.40, 90),
    ParkingArea('127', -03.27, -22.40, 90),
    ParkingArea('128', -00.89, -22.40, 90),
    ParkingArea('129', +02.46, -22.40, 90),
    ParkingArea('130', +04.82, -22.40, 90),
    ParkingArea('131', +07.20, -22.40, 90),
    ParkingArea('132', +10.54, -22.40, 90),
    ParkingArea('133', +12.91, -22.40, 90),
    ParkingArea('134', +15.20, -22.40, 90),
    ParkingArea('135', +26.66, -22.40, 90),
    ParkingArea('136', +29.09, -22.40, 90),
    ParkingArea('137', +31.48, -22.40, 90),
    ParkingArea('138', +34.86, -22.40, 90),
    ParkingArea('139', +37.17, -22.40, 90),
    ParkingArea('140', +42.95, -22.40, 90),
    ParkingArea('141', +45.33, -22.40, 90),
    ParkingArea('142', +47.67, -22.40, 90),
    ParkingArea('143', +51.06, -22.40, 90),
    ParkingArea('144', +53.41, -22.40, 90),
    ParkingArea('145', +55.70, -22.40, 90),
    ParkingArea('146', +55.75, -11.55, 270),
    ParkingArea('147', +53.41, -11.55, 270),
    ParkingArea('148', +51.06, -11.55, 270),
    ParkingArea('149', +47.67, -11.55, 270),
    ParkingArea('150', +45.33, -11.55, 270),
    ParkingArea('151', +42.95, -11.55, 270),
    ParkingArea('152', +37.17, -11.13, 270),
    ParkingArea('153', +34.86, -11.13, 270),
    ParkingArea('154', +31.48, -11.13, 270),
    ParkingArea('155', +29.09, -11.13, 270),
    ParkingArea('156', +26.66, -11.13, 270),
    ParkingArea('157', +15.28, -11.13, 270),
    ParkingArea('158', +12.92, -11.13, 270),
    ParkingArea('159', -00.88, -11.13, 270),
    ParkingArea('160', -03.27, -11.13, 270),
    ParkingArea('161', -05.67, -11.13, 270),
    ParkingArea('162', -13.77, -11.13, 270),
    ParkingArea('163', -17.05, -11.13, 270),
    ParkingArea('164', -19.49, -11.13, 270),
    ParkingArea('165', -21.86, -11.13, 270),
    ParkingArea('166', -24.32, -08.22, 90),
    ParkingArea('167', -21.83, -05.13, 90),
    ParkingArea('168', -19.49, -05.13, 90),
    ParkingArea('169', -17.10, -05.13, 90),
    ParkingArea('170', -13.85, -05.13, 90),
    ParkingArea('171', +54.70, -07.84, 0),
    ParkingArea('172', +56.22, +01.76, 270),
    ParkingArea('173', +50.07, +06.58, 0),
    ParkingArea('174', +44.29, +06.58, 0),
    ParkingArea('175', +36.55, +06.58, 0),
    ParkingArea('176', +29.19, +06.58, 0),
    ParkingArea('177', +09.24, +06.58, 0),
    ParkingArea('178', +03.93, +06.58, 0),
    ParkingArea('179', -01.44, +06.58, 0),
    ParkingArea('180', -06.75, +06.58, 0),
    ParkingArea('181', -12.06, +06.58, 0),
    ParkingArea('182', -24.16, +16.27, 270),
    ParkingArea('183', -21.77, +16.27, 270),
    ParkingArea('184', -17.51, +16.27, 270),
    ParkingArea('185', -15.17, +16.27, 270),
    ParkingArea('186', -11.99, +16.27, 270),
    ParkingArea('187', -09.60, +16.27, 270),
    ParkingArea('188', -05.58, +16.27, 270),
    ParkingArea('189', -03.27, +16.27, 270),
    ParkingArea('190', -00.00, +16.27, 270),
    ParkingArea('191', +02.46, +16.27, 270),
    ParkingArea('192', +06.42, +16.27, 270),
    ParkingArea('193', +08.73, +16.27, 270),
    ParkingArea('194', +11.98, +16.27, 270),
    ParkingArea('195', +14.35, +16.27, 270),
    ParkingArea('196', +23.98, +16.27, 270),
    ParkingArea('197', +26.34, +16.27, 270),
    ParkingArea('198', +30.36, +16.27, 270),
    ParkingArea('199', +32.65, +16.27, 270),
    ParkingArea('200', +35.94, +16.27, 270),
    ParkingArea('201', +38.31, +16.27, 270),
    ParkingArea('202', +55.39, +15.69, 0),
    ParkingArea('203', +30.36, +21.37, 90),
    ParkingArea('204', +26.34, +21.37, 90),
    ParkingArea('205', +23.98, +21.37, 90),
    ParkingArea('206', +14.28, +21.37, 90),
    ParkingArea('207', +11.98, +21.37, 90),
    ParkingArea('208', +08.73, +21.37, 90),
    ParkingArea('209', +06.42, +21.37, 90),
    ParkingArea('210', +02.31, +21.37, 90),
    ParkingArea('211', -00.00, +21.37, 90),
    ParkingArea('212', -03.27, +21.37, 90),
    ParkingArea('213', -05.58, +21.37, 90),
    ParkingArea('214', -09.60, +21.37, 90),
    ParkingArea('215', -11.99, +21.37, 90),
    ParkingArea('216', -15.17, +21.37, 90),
    ParkingArea('217', -17.51, +21.37, 90),
    ParkingArea('218', -21.77, +21.37, 90),
    ParkingArea('219', -24.16, +21.37, 90),
    ParkingArea('220', -21.84, +32.52, 270),
    ParkingArea('221', -19.48, +32.52, 270),
    ParkingArea('222', -17.10, +32.52, 270),
    ParkingArea('223', -13.73, +32.52, 270),
    ParkingArea('224', -11.37, +32.52, 270),
    ParkingArea('225', -09.05, +32.52, 270),
    ParkingArea('226', -05.66, +32.52, 270),
    ParkingArea('227', -03.27, +32.52, 270),
    ParkingArea('228', -00.95, +32.52, 270),
    ParkingArea('229', +02.46, +32.52, 270),
    ParkingArea('230', +04.82, +32.52, 270),
    ParkingArea('231', +07.12, +32.52, 270),
    ParkingArea('232', +10.54, +32.52, 270),
    ParkingArea('233', +12.91, +32.52, 270),
    ParkingArea('234', +15.30, +32.52, 270),
    ParkingArea('235', +24.27, +35.18, 90),
    ParkingArea('236', +26.71, +32.52, 270),
    ParkingArea('237', +29.09, +32.52, 270),
    ParkingArea('238', +31.42, +32.52, 270),
    ParkingArea('239', +34.86, +32.52, 270),
    ParkingArea('240', +37.17, +32.52, 270),
    ParkingArea('241', +39.62, +32.52, 270),
    ParkingArea('242', +42.95, +32.52, 270),
    ParkingArea('243', +45.33, +32.52, 270),
    ParkingArea('244', +47.60, +32.52, 270),
    ParkingArea('245', +51.06, +32.52, 270),
    ParkingArea('246', +53.41, +32.52, 270),
    ParkingArea('247', +55.69, +32.52, 270),
    ParkingArea('248', +55.78, +38.24, 90),
    ParkingArea('249', +53.41, +38.24, 90),
    ParkingArea('250', +51.06, +38.24, 90),
    ParkingArea('251', +47.67, +38.24, 90),
    ParkingArea('252', +45.33, +38.24, 90),
    ParkingArea('253', +42.95, +38.24, 90),
    ParkingArea('254', +39.62, +38.24, 90),
    ParkingArea('255', +37.17, +38.24, 90),
    ParkingArea('256', +34.86, +38.24, 90),
    ParkingArea('257', +31.42, +38.24, 90),
    ParkingArea('258', +29.09, +38.24, 90),
    ParkingArea('259', +26.71, +38.24, 90),
    ParkingArea('260', +15.28, +38.24, 90),
    ParkingArea('261', +12.91, +38.24, 90),
    ParkingArea('262', +10.54, +38.24, 90),
    ParkingArea('263', +07.12, +38.24, 90),
    ParkingArea('264', +04.82, +38.24, 90),
    ParkingArea('265', +02.46, +38.24, 90),
    ParkingArea('266', -00.95, +38.24, 90),
    ParkingArea('267', -03.27, +38.24, 90),
    ParkingArea('268', -05.66, +38.24, 90),
    ParkingArea('269', -09.05, +38.24, 90),
    ParkingArea('270', -11.37, +38.24, 90),
    ParkingArea('271', -13.73, +38.24, 90),
    ParkingArea('272', -17.10, +38.24, 90),
    ParkingArea('273', -19.48, +38.24, 90),
    ParkingArea('274', -21.84, +38.24, 90),
    ParkingArea('275', -24.27, +35.65, 270),
    ParkingArea('276', -33.97, -54.84, 0),
    ParkingArea('277', -33.97, -51.51, 0),
    ParkingArea('278', -33.97, -49.14, 0),
    ParkingArea('279', -33.97, -46.78, 0),
    ParkingArea('280', -33.97, -41.00, 0),
    ParkingArea('281', -33.97, -38.64, 0),
    ParkingArea('282', -33.97, -35.32, 0),
    ParkingArea('283', -33.97, -32.95, 0),
    ParkingArea('284', -33.97, -30.59, 0),
    ParkingArea('285', -33.97, -27.16, 0),
    ParkingArea('286', -33.97, -24.79, 0),
    ParkingArea('287', -33.97, -22.43, 0),
    ParkingArea('288', -33.97, -19.13, 0),
    ParkingArea('289', -33.97, -16.76, 0),
    ParkingArea('290', -33.97, -14.40, 0),
    ParkingArea('291', -33.97, -11.03, 0),
    ParkingArea('292', -33.97, -08.67, 0),
    ParkingArea('293', -33.97, -06.31, 0),
    ParkingArea('294', -33.97, +26.83, 0),
    ParkingArea('295', -33.97, +29.19, 0),
    ParkingArea('296', -33.97, +32.38, 0),
    ParkingArea('297', -33.97, +34.74, 0),
    ParkingArea('298', -33.97, +37.10, 0),
    ParkingArea('299', -33.97, +40.53, 0),
    ParkingArea('300', -33.97, +42.86, 0),
    ParkingArea('301', -33.97, +45.32, 0),
    ParkingArea('302', -29.98, +49.25, 270),
    ParkingArea('303', -27.58, +49.25, 270),
    ParkingArea('304', -25.25, +49.25, 270),
    ParkingArea('305', -21.85, +49.25, 270),
    ParkingArea('306', -19.48, +49.25, 270),
    ParkingArea('307', -17.10, +49.25, 270),
    ParkingArea('308', -13.76, +49.25, 270),
    ParkingArea('309', -11.37, +49.25, 270),
    ParkingArea('310', -09.00, +49.25, 270),
    ParkingArea('311', -05.66, +49.25, 270),
    ParkingArea('312', -03.27, +49.25, 270),
    ParkingArea('313', -00.89, +49.25, 270),
    ParkingArea('314', +02.46, +49.25, 270),
    ParkingArea('315', +04.82, +49.25, 270),
    ParkingArea('316', +07.20, +49.25, 270),
    ParkingArea('317', +10.54, +49.25, 270),
    ParkingArea('318', +12.91, +49.25, 270),
    ParkingArea('319', +15.28, +49.25, 270),
    ParkingArea('320', +18.68, +49.25, 270),
    ParkingArea('321', +21.06, +49.25, 270),
    ParkingArea('322', +23.43, +49.25, 270),
    ParkingArea('323', +26.79, +49.25, 270),
    ParkingArea('324', +29.19, +49.25, 270),
    ParkingArea('325', +31.56, +49.25, 270),
    ParkingArea('326', +34.86, +49.25, 270),
    ParkingArea('327', +37.17, +49.25, 270),
    ParkingArea('328', +39.62, +49.25, 270),
    ParkingArea('329', +42.95, +49.25, 270),
    ParkingArea('330', +45.33, +49.41, 270),
    ParkingArea('331', +51.26, +49.41, 270),
    ParkingArea('332', +59.37, +49.25, 270),
    ParkingArea('333', +61.75, +49.25, 270, no_random_pose=True),
    ParkingArea('334', +65.70, +26.82, 180),
    ParkingArea('335', +65.70, +24.45, 180),
    ParkingArea('336', +65.70, +20.14, 180),
    ParkingArea('337', +65.70, +17.75, 180),
    ParkingArea('338', +65.70, +15.36, 180),
    ParkingArea('339', +65.70, +11.61, 180),
    ParkingArea('340', +65.70, +09.22, 180),
    ParkingArea('341', +65.70, +06.83, 180),
    ParkingArea('342', +65.70, +02.93, 180),
    ParkingArea('343', +65.70, +00.51, 180),
    ParkingArea('344', +65.70, -01.83, 180),
    ParkingArea('345', +65.70, -06.26, 180),
    ParkingArea('346', +65.70, -08.63, 180),
    ParkingArea('347', +65.70, -11.00, 180),
    ParkingArea('348', +65.70, -14.41, 180),
    ParkingArea('349', +65.70, -16.78, 180),
    ParkingArea('350', +65.70, -19.15, 180),
    ParkingArea('351', +65.70, -22.47, 180),
    ParkingArea('352', +65.70, -24.84, 180),
    ParkingArea('353', +65.70, -27.21, 180),
    ParkingArea('354', +65.70, -30.57, 180),
    ParkingArea('355', +65.70, -32.97, 180),
    ParkingArea('356', +65.70, -35.33, 180),
    ParkingArea('357', +65.70, -38.70, 180),
    ParkingArea('358', +65.70, -41.07, 180),
    ParkingArea('359', +65.70, -43.44, 180),
    ParkingArea('360', +65.70, -46.81, 180),
    ParkingArea('361', +65.70, -49.18, 180),
    ParkingArea('362', +65.70, -51.55, 180),
    ParkingArea('363', +65.70, -54.92, 180),
    ParkingArea('364', +65.70, -57.29, 180),
    ParkingArea('365', +65.70, -59.81, 180),
]

AVAILABLE_VEHICLE_NAME = [
    'vehicle.audi.a2',
    'vehicle.nissan.micra',
    'vehicle.audi.tt',
    'vehicle.mercedes.coupe_2020',
    'vehicle.bmw.grandtourer',
    # 'vehicle.harley-davidson.low_rider',  # NO MOTORCYCLES
    # 'vehicle.ford.ambulance',  # TOO LARGE
    'vehicle.micro.microlino',
    # 'vehicle.carlamotors.firetruck',  # TOO LARGE
    # 'vehicle.carlamotors.carlacola',   # TOO LARGE
    # 'vehicle.carlamotors.european_hgv',  # TOO LARGE
    'vehicle.ford.mustang',
    'vehicle.chevrolet.impala',
    'vehicle.lincoln.mkz_2020',
    'vehicle.citroen.c3',
    'vehicle.dodge.charger_police',
    'vehicle.nissan.patrol',
    'vehicle.jeep.wrangler_rubicon',
    'vehicle.mini.cooper_s',
    'vehicle.mercedes.coupe',
    'vehicle.dodge.charger_2020',
    'vehicle.ford.crown',
    'vehicle.seat.leon',
    'vehicle.toyota.prius',
    # 'vehicle.yamaha.yzf',  # NO MOTORCYCLES
    # 'vehicle.kawasaki.ninja',  # NO MOTORCYCLES
    # 'vehicle.bh.crossbike',  # NO MOTORCYCLES
    'vehicle.mitsubishi.fusorosa',
    'vehicle.tesla.model3',
    # 'vehicle.gazelle.omafiets',
    # 'vehicle.tesla.cybertruck', # TOO LARGE
    # 'vehicle.diamondback.century',
    'vehicle.mercedes.sprinter',
    'vehicle.audi.etron',
    'vehicle.volkswagen.t2',
    'vehicle.lincoln.mkz_2017',
    # 'vehicle.dodge.charger_police_2020',  # NO POLICE CAR
    # 'vehicle.vespa.zx125',  # NO MOTORCYCLES
    # 'vehicle.mini.cooper_s_2021',  # NO OLD VEHICLE
    # 'vehicle.nissan.patrol_2021',  # NO OLD VEHICLE
    # 'vehicle.volkswagen.t2_2021',  # NO OLD VEHICLE
    # 'vehicle.byd.qinpro',  # NO TEST VEHICLE
]

def create_vehicles(client):
    print("loaded world...")
    world = client.get_world()  # type: carla.World

    print("get world...")
    actors = []

    num_to_spawn = 150
    num_of_moving_vehicles = 20  # 控制移动车辆数量
    tm_speed_variation = 30   # 车速变化百分比（正数减速，负数加速）

    # Get random sequence of parking spots
    random.shuffle(AVAILABLE_PARKING_AREAS)
    parking = AVAILABLE_PARKING_AREAS

    # Spawn vehicles
    print("Start spawn vehicles...")
    spawn_counter = 0
    spawn_offset = 0
    retry = 0
    max_retry = 5
    while len(actors) < num_to_spawn:
        if retry > max_retry:
            spawn_offset += 1
            # print(f'Failed to spawn vehicle (name={parking[spawn_counter].name}), skipping to next parking spot...')

        bp = world.get_blueprint_library().find(random.choice(AVAILABLE_VEHICLE_NAME))
        bp.set_attribute('color', random.choice(bp.get_attribute('color').recommended_values))

        tf = parking[spawn_counter + spawn_offset].get_spawn_point(rand_pos_x=0.2, rand_pos_y=0.2, rand_yaw=5)
        vehicle = world.try_spawn_actor(bp, tf)
        if vehicle is not None:
            actors.append(vehicle)
            spawn_counter += 1
            retry = 0
            # print(f'Spawned {vehicle.type_id} at {tf}')
        else:
            # print(f'Failed to spawn vehicle (name={parking[spawn_counter].name}), retrying...')
            retry += 1

    print(f'Spawned {len(actors)} vehicles')

    vehicles = []

    # 初始化Traffic Manager
    tm = client.get_trafficmanager()
    tm_port = tm.get_port()
    # tm.set_synchronous_mode(True)  # 设置为同步模式
    
    # 设置全局交通参数
    tm.global_percentage_speed_difference(tm_speed_variation)

    # 获取所有车辆蓝图并过滤
    vehicle_blueprints = world.get_blueprint_library().filter('vehicle.*')
    vehicle_blueprints = [bp for bp in vehicle_blueprints if int(bp.get_attribute('number_of_wheels')) == 4]
    
    # 获取地图生成点
    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    
    # 生成移动车辆
    spawn_count = 0
    for i in range(num_of_moving_vehicles):
        # 随机选择车辆蓝图
        bp = random.choice(vehicle_blueprints)
        
        # 设置车辆颜色
        if bp.has_attribute('color'):
            color = random.choice(bp.get_attribute('color').recommended_values)
            bp.set_attribute('color', color)
        
        # 尝试生成车辆
        transform = spawn_points[i % len(spawn_points)]  # 循环使用生成点
        vehicle = world.try_spawn_actor(bp, transform)
        
        if vehicle:
            try:
                # 启用自动驾驶并连接到交通管理器
                vehicle.set_autopilot(True, tm_port)

                vehicles.append(vehicle)
                spawn_count += 1
                # print(f'Spawned moving vehicle {vehicle.type_id} at {transform.location}.')
            except Exception as e:
                # print(f'Failed to set vehicle: {str(e)}')
                vehicle.destroy()
        # else:
            # print(f'Failed to spawn vehicle at {transform.location}.')

    print(f'Created {len(vehicles)} moving vehicles.')
    return actors, vehicles

    frame = 0
    while True:
        try:
            
            world.tick()
            time.sleep(0.1)

            if frame % 100 == 0:
                current_time = world.get_snapshot().timestamp.elapsed_seconds
                moving_speeds = [v.get_velocity().length() for v in vehicles]
                print(f"[Frame {frame}] 仿真时间: {current_time:.1f}s | "
                      f"移动车辆平均速度: {sum(moving_speeds)/len(moving_speeds):.2f}m/s")
        except KeyboardInterrupt:
            print('KeyboardInterrupt detected, cleaning up...')
            break
        frame = frame + 1

    for actor in actors:
        actor.destroy()
    for vehicle in vehicles:
        actor.destroy()

    print('All actors destroyed, exiting...')
    print('Goodbye!')

if __name__ == '__main__':
    client = carla.Client('localhost', 2000)
    
    create_vehicles(client)

